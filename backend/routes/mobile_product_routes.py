import asyncio
import csv
import io
import re
import time
from datetime import datetime
from datetime import timedelta
from typing import Any, Dict, Optional
from uuid import uuid4

import requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query

from mongo_auth import get_current_user
from mongo_db import get_database
from services.amazon_service import AmazonService
from services.flipkart_service import FlipkartService
from services.croma_service import CromaService
from mongo_schemas import (
    ImportSheetRequest,
    ProductCreateRequest,
    ProductResponse,
    ProductPrices,
    UpdatePricesRequest,
)
from mongo_scraper import scrape_single_platform, choose_best, now_utc

router = APIRouter(tags=["mobile-products"])

CACHE_TTL_MINUTES = 180
_REFRESH_JOBS: Dict[str, Dict[str, Any]] = {}
PER_PRODUCT_TIMEOUT_SECONDS = 45
PER_PLATFORM_TIMEOUT_SECONDS = 12
MIN_PHONE_PRICE = 5000


def _next_refresh_timestamp(previous: Any) -> datetime:
    now = now_utc()
    if not isinstance(previous, datetime):
        return now

    prev = previous
    if prev.tzinfo is None:
        prev = prev.replace(tzinfo=now.tzinfo)

    # Ensure visible progression for rapid consecutive retries.
    if now <= prev:
        return prev + timedelta(seconds=1)
    return now


def _normalize_doc(doc: Dict[str, Any]) -> ProductResponse:
    prices = _sanitize_prices(doc.get("category"), dict(doc.get("prices") or {}))
    best_price, best_platform = choose_best(prices)
    return ProductResponse(
        id=str(doc.get("_id")),
        category=doc.get("category", ""),
        brand=doc.get("brand", ""),
        model=doc.get("model", ""),
        variant_name=doc.get("variant_name", ""),
        amazon_url=doc.get("amazon_url"),
        flipkart_url=doc.get("flipkart_url"),
        croma_url=doc.get("croma_url"),
        prices=ProductPrices(
            amazon=prices.get("amazon"),
            flipkart=prices.get("flipkart"),
            croma=prices.get("croma"),
        ),
        image_url=doc.get("image_url"),
        best_price=best_price,
        best_platform=best_platform,
        specifications=doc.get("specifications", {}),
        last_updated=doc.get("last_updated"),
    )


def _doc_group_key(doc: Dict[str, Any]) -> str:
    a = str(doc.get("amazon_url") or "").strip().lower()
    f = str(doc.get("flipkart_url") or "").strip().lower()
    c = str(doc.get("croma_url") or "").strip().lower()
    if a or f or c:
        return f"url::{a}|{f}|{c}"

    brand = str(doc.get("brand") or "").strip().lower()
    model = str(doc.get("model") or "").strip().lower()
    variant = str(doc.get("variant_name") or "").strip().lower()
    return f"meta::{brand}|{model}|{variant}"


def _is_better_doc(candidate: Dict[str, Any], current: Dict[str, Any]) -> bool:
    cand_price = candidate.get("best_price")
    curr_price = current.get("best_price")

    if cand_price is not None and curr_price is None:
        return True
    if cand_price is None and curr_price is not None:
        return False

    cand_updated = candidate.get("last_updated")
    curr_updated = current.get("last_updated")
    if cand_updated and curr_updated:
        return cand_updated > curr_updated
    return bool(cand_updated) and not bool(curr_updated)


def _is_cache_fresh(doc: Dict[str, Any], force_refresh: bool) -> bool:
    if force_refresh:
        return False

    # Never consider records with unavailable pricing as fresh.
    if doc.get("best_price") is None:
        return False

    prices = dict(doc.get("prices") or {})
    if (
        prices.get("amazon") is None
        and prices.get("flipkart") is None
        and prices.get("croma") is None
    ):
        return False

    last_updated = doc.get("last_updated")
    if not last_updated:
        return False
    if isinstance(last_updated, datetime) and last_updated.tzinfo is None:
        last_updated = last_updated.replace(tzinfo=now_utc().tzinfo)
    return (now_utc() - last_updated) < timedelta(minutes=CACHE_TTL_MINUTES)


def _merge_scrape(primary: Dict[str, Any], fallback: Dict[str, Any]) -> Dict[str, Any]:
    merged = {
        "title": primary.get("title") or fallback.get("title"),
        "price": primary.get("price") if primary.get("price") is not None else fallback.get("price"),
        "image_url": primary.get("image_url") or fallback.get("image_url"),
        "specifications": dict(primary.get("specifications") or {}),
    }
    if not merged["specifications"]:
        merged["specifications"] = dict(fallback.get("specifications") or {})
    return merged


def _scrape_with_accuracy(platform: str, url: str, allow_selenium_retry: bool = True) -> Dict[str, Any]:
    if not url:
        return {"title": None, "price": None, "image_url": None, "specifications": {}}

    fast = scrape_single_platform(platform, url, allow_selenium=False)

    # Retry with Selenium only for pricing/title gaps; missing image alone
    # should not trigger a heavy fallback.
    needs_retry = (
        fast.get("price") is None
        or not fast.get("title")
    )
    if not needs_retry:
        return fast

    if not allow_selenium_retry:
        return fast

    accurate = scrape_single_platform(platform, url, allow_selenium=True)
    return _merge_scrape(fast, accurate)


def _resolved_price(new_value: Any, previous_value: Any) -> Any:
    return new_value if new_value is not None else previous_value


def _sanitize_price(category: Optional[str], value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None

    if numeric <= 0:
        return None

    # Current dataset is phone-focused; tiny values are usually EMI/offer artifacts.
    cat = str(category or "").strip().lower()
    if re.search(r"\b(phone|mobile|smart\s*phone)s?\b", cat):
        if numeric < MIN_PHONE_PRICE:
            return None

    return numeric


def _sanitize_prices(category: Optional[str], prices: Dict[str, Any]) -> Dict[str, Optional[float]]:
    return {
        "amazon": _sanitize_price(category, prices.get("amazon")),
        "flipkart": _sanitize_price(category, prices.get("flipkart")),
        "croma": _sanitize_price(category, prices.get("croma")),
    }


def _prefer_variant_name(scraped_title: Optional[str], payload_variant_name: str) -> str:
    scraped = (scraped_title or "").strip()
    payload = (payload_variant_name or "").strip()
    if not scraped:
        return payload

    scraped_words = len(scraped.split())
    payload_words = len(payload.split())

    # Avoid replacing strong user-provided variant names with weak URL-derived fallback titles.
    if payload and payload_words >= 4 and scraped_words <= 4:
        return payload
    if payload and len(scraped) < 12:
        return payload

    return scraped


def _query_seed(doc: Dict[str, Any]) -> str:
    parts = [
        str(doc.get("brand") or "").strip(),
        str(doc.get("model") or "").strip(),
        str(doc.get("variant_name") or "").strip(),
    ]
    seed = " ".join([p for p in parts if p])
    seed = " ".join(seed.split())
    return seed[:120]


def _search_platform_price_by_query(platform: str, query: str) -> Dict[str, Any]:
    if not query:
        return {"price": None, "title": None, "image_url": None}

    try:
        if platform == "amazon":
            results = AmazonService().search_products(query, max_results=5)
        elif platform == "flipkart":
            results = FlipkartService().search_products(query, max_results=5)
        else:
            results = CromaService().search_products(query, max_results=5)

        for item in results:
            price = item.get("price")
            if price is None:
                continue
            return {
                "price": price,
                "title": item.get("title"),
                "image_url": item.get("image_url"),
            }
    except Exception:
        pass

    return {"price": None, "title": None, "image_url": None}


async def _safe_scrape_platform(platform: str, url: str, allow_selenium_retry: bool = False) -> Dict[str, Any]:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_scrape_with_accuracy, platform, url, allow_selenium_retry),
            timeout=PER_PLATFORM_TIMEOUT_SECONDS,
        )
    except Exception:
        return {"title": None, "price": None, "image_url": None, "specifications": {}}


async def _safe_query_price(platform: str, seed: str) -> Dict[str, Any]:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(_search_platform_price_by_query, platform, seed),
            timeout=PER_PLATFORM_TIMEOUT_SECONDS,
        )
    except Exception:
        return {"price": None, "title": None, "image_url": None}


async def _refresh_product_doc(db, doc: Dict[str, Any]) -> None:
    amazon, flipkart, croma = await asyncio.gather(
        _safe_scrape_platform("amazon", doc.get("amazon_url") or "", False),
        _safe_scrape_platform("flipkart", doc.get("flipkart_url") or "", False),
        _safe_scrape_platform("croma", doc.get("croma_url") or "", False),
    )

    existing_prices = dict(doc.get("prices") or {})

    prices = {
        "amazon": _resolved_price(amazon.get("price"), existing_prices.get("amazon")),
        "flipkart": _resolved_price(flipkart.get("price"), existing_prices.get("flipkart")),
        "croma": _resolved_price(croma.get("price"), existing_prices.get("croma")),
    }
    prices = _sanitize_prices(doc.get("category"), prices)

    # If direct-link scraping misses any platform, use query-based platform search
    # selectively for those missing platforms.
    missing_platforms = [platform for platform, value in prices.items() if value is None]
    if missing_platforms:
        seed = _query_seed(doc)
        hits = await asyncio.gather(*[_safe_query_price(platform, seed) for platform in missing_platforms])
        query_hits = dict(zip(missing_platforms, hits))

        if prices["amazon"] is None:
            prices["amazon"] = (query_hits.get("amazon") or {}).get("price")
        if prices["flipkart"] is None:
            prices["flipkart"] = (query_hits.get("flipkart") or {}).get("price")
        if prices["croma"] is None:
            prices["croma"] = (query_hits.get("croma") or {}).get("price")
        prices = _sanitize_prices(doc.get("category"), prices)

        if "amazon" in query_hits:
            amazon = _merge_scrape(amazon, query_hits["amazon"])
        if "flipkart" in query_hits:
            flipkart = _merge_scrape(flipkart, query_hits["flipkart"])
        if "croma" in query_hits:
            croma = _merge_scrape(croma, query_hits["croma"])

    best_price, best_platform = choose_best(prices)

    image_url = doc.get("image_url") or amazon.get("image_url") or flipkart.get("image_url") or croma.get("image_url")

    specs = dict(doc.get("specifications") or {})
    for source in (amazon, flipkart, croma):
        for k, v in (source.get("specifications") or {}).items():
            if k not in specs and v:
                specs[k] = v

    refresh_time = _next_refresh_timestamp(doc.get("last_updated"))

    await db.products.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "prices": prices,
                "best_price": best_price,
                "best_platform": best_platform,
                "image_url": image_url,
                "specifications": specs,
                "last_updated": refresh_time,
            }
        },
    )


async def _refresh_product_platform(db, doc: Dict[str, Any], platform: str) -> None:
    if platform not in {"amazon", "flipkart", "croma"}:
        raise ValueError("Unsupported platform")

    platform_url = doc.get(f"{platform}_url") or ""
    scraped = await _safe_scrape_platform(platform, platform_url, False)

    existing_prices = dict(doc.get("prices") or {})
    prices = {
        "amazon": existing_prices.get("amazon"),
        "flipkart": existing_prices.get("flipkart"),
        "croma": existing_prices.get("croma"),
    }
    prices[platform] = _resolved_price(scraped.get("price"), existing_prices.get(platform))
    prices = _sanitize_prices(doc.get("category"), prices)

    if prices.get(platform) is None:
        seed = _query_seed(doc)
        hit = await _safe_query_price(platform, seed)
        prices[platform] = hit.get("price")
        prices = _sanitize_prices(doc.get("category"), prices)
        scraped = _merge_scrape(scraped, hit)

    best_price, best_platform = choose_best(prices)

    image_url = doc.get("image_url") or scraped.get("image_url")
    specs = dict(doc.get("specifications") or {})
    for k, v in (scraped.get("specifications") or {}).items():
        if k not in specs and v:
            specs[k] = v

    refresh_time = _next_refresh_timestamp(doc.get("last_updated"))

    await db.products.update_one(
        {"_id": doc["_id"]},
        {
            "$set": {
                "prices": prices,
                "best_price": best_price,
                "best_platform": best_platform,
                "image_url": image_url,
                "specifications": specs,
                "last_updated": refresh_time,
            }
        },
    )


async def _run_quick_refresh_job(job_id: str, force_refresh: bool, limit: int) -> None:
    db = get_database()
    _REFRESH_JOBS[job_id] = {
        "status": "running",
        "updated": 0,
        "skipped_fresh": 0,
        "processed": 0,
        "limit": limit,
        "started_at": now_utc(),
    }

    try:
        priority_query = {
            "$or": [
                {"best_price": None},
                {"prices.amazon": None},
                {"prices.flipkart": None},
                {"prices.croma": None},
            ]
        }
        docs = await db.products.find(priority_query).sort("last_updated", 1).to_list(length=limit)

        updated = 0
        skipped_fresh = 0
        failed = 0
        timed_out = 0

        for index, doc in enumerate(docs, start=1):
            if _is_cache_fresh(doc, force_refresh):
                skipped_fresh += 1
                _REFRESH_JOBS[job_id].update(
                    {
                        "updated": updated,
                        "skipped_fresh": skipped_fresh,
                        "failed": failed,
                        "timed_out": timed_out,
                        "processed": index,
                    }
                )
                continue

            try:
                await asyncio.wait_for(_refresh_product_doc(db, doc), timeout=PER_PRODUCT_TIMEOUT_SECONDS)
                updated += 1
            except asyncio.TimeoutError:
                timed_out += 1
            except Exception as exc:
                failed += 1
                _REFRESH_JOBS[job_id]["last_error"] = str(exc)

            _REFRESH_JOBS[job_id].update(
                {
                    "updated": updated,
                    "skipped_fresh": skipped_fresh,
                    "failed": failed,
                    "timed_out": timed_out,
                    "processed": index,
                }
            )

        _REFRESH_JOBS[job_id].update(
            {
                "status": "completed",
                "updated": updated,
                "skipped_fresh": skipped_fresh,
                "failed": failed,
                "timed_out": timed_out,
                "processed": len(docs),
                "finished_at": now_utc(),
            }
        )
    except Exception as exc:
        _REFRESH_JOBS[job_id].update(
            {
                "status": "failed",
                "error": str(exc),
                "finished_at": now_utc(),
            }
        )


@router.get("/products", response_model=list[ProductResponse])
async def get_products(
    search: Optional[str] = Query(default=None),
    category: Optional[str] = Query(default=None),
    brand: Optional[str] = Query(default=None),
):
    db = get_database()
    q: Dict[str, Any] = {}

    if category:
        q["category"] = {"$regex": f"^{category}$", "$options": "i"}
    if brand:
        q["brand"] = {"$regex": f"^{brand}$", "$options": "i"}
    if search:
        q["$text"] = {"$search": search}

    cursor = db.products.find(q).sort("best_price", 1)
    docs = await cursor.to_list(length=1000)

    deduped: Dict[str, Dict[str, Any]] = {}
    for doc in docs:
        key = _doc_group_key(doc)
        existing = deduped.get(key)
        if existing is None or _is_better_doc(doc, existing):
            deduped[key] = doc

    final_docs = list(deduped.values())

    for doc in final_docs:
        prices = _sanitize_prices(doc.get("category"), dict(doc.get("prices") or {}))
        best_price, best_platform = choose_best(prices)
        doc["prices"] = prices
        doc["best_price"] = best_price
        doc["best_platform"] = best_platform

    final_docs.sort(key=lambda d: (d.get("best_price") is None, d.get("best_price") or float("inf")))
    return [_normalize_doc(d) for d in final_docs]


@router.get("/admin/ping-db")
async def ping_db(_: dict = Depends(get_current_user)):
    db = get_database()
    started = time.perf_counter()
    ping_ok = False
    error: Optional[str] = None

    try:
        await db.command({"ping": 1})
        ping_ok = True
    except Exception as exc:
        error = str(exc)

    elapsed_ms = round((time.perf_counter() - started) * 1000, 2)

    products_count: Optional[int] = None
    users_count: Optional[int] = None
    count_error: Optional[str] = None

    try:
        products_count = await db.products.estimated_document_count()
        users_count = await db.users.estimated_document_count()
    except Exception as exc:
        count_error = str(exc)

    return {
        "db_ping_ok": ping_ok,
        "db_ping_latency_ms": elapsed_ms,
        "products_count": products_count,
        "users_count": users_count,
        "count_error": count_error,
        "error": error,
        "timestamp": now_utc(),
    }


@router.get("/product/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    db = get_database()
    doc = await db.products.find_one({"_id": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    prices = _sanitize_prices(doc.get("category"), dict(doc.get("prices") or {}))
    missing_platforms = [platform for platform, value in prices.items() if value is None]

    if missing_platforms:
        seed = _query_seed(doc)
        if seed:
            hits = await asyncio.gather(*[_safe_query_price(platform, seed) for platform in missing_platforms])
            query_hits = dict(zip(missing_platforms, hits))

            changed = False
            for platform in missing_platforms:
                hit_price = (query_hits.get(platform) or {}).get("price")
                if hit_price is not None:
                    prices[platform] = hit_price
                    changed = True

            prices = _sanitize_prices(doc.get("category"), prices)
            best_price, best_platform = choose_best(prices)

            if changed:
                image_url = doc.get("image_url")
                if not image_url:
                    for platform in ("amazon", "flipkart", "croma"):
                        image_url = image_url or (query_hits.get(platform) or {}).get("image_url")

                await db.products.update_one(
                    {"_id": product_id},
                    {
                        "$set": {
                            "prices": prices,
                            "best_price": best_price,
                            "best_platform": best_platform,
                            "image_url": image_url,
                            "last_updated": _next_refresh_timestamp(doc.get("last_updated")),
                        }
                    },
                )

                doc["prices"] = prices
                doc["best_price"] = best_price
                doc["best_platform"] = best_platform
                doc["image_url"] = image_url

    return _normalize_doc(doc)


@router.post("/product/{product_id}/retry-prices", response_model=ProductResponse)
async def retry_product_prices(product_id: str):
    db = get_database()
    doc = await db.products.find_one({"_id": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await asyncio.wait_for(_refresh_product_doc(db, doc), timeout=PER_PRODUCT_TIMEOUT_SECONDS)
    except Exception:
        # Keep endpoint resilient; still stamp refresh attempt time for UI visibility.
        await db.products.update_one(
            {"_id": product_id},
            {"$set": {"last_updated": _next_refresh_timestamp(doc.get("last_updated"))}},
        )

    latest = await db.products.find_one({"_id": product_id})
    if not latest:
        raise HTTPException(status_code=404, detail="Product not found")
    return _normalize_doc(latest)


@router.post("/product/{product_id}/retry-platform/{platform}", response_model=ProductResponse)
async def retry_product_platform_price(product_id: str, platform: str):
    platform = str(platform or "").strip().lower()
    if platform not in {"amazon", "flipkart", "croma"}:
        raise HTTPException(status_code=400, detail="Invalid platform")

    db = get_database()
    doc = await db.products.find_one({"_id": product_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")

    try:
        await asyncio.wait_for(_refresh_product_platform(db, doc, platform), timeout=PER_PRODUCT_TIMEOUT_SECONDS)
    except Exception:
        await db.products.update_one(
            {"_id": product_id},
            {"$set": {"last_updated": _next_refresh_timestamp(doc.get("last_updated"))}},
        )

    latest = await db.products.find_one({"_id": product_id})
    if not latest:
        raise HTTPException(status_code=404, detail="Product not found")
    return _normalize_doc(latest)


@router.post("/scrape-product", response_model=ProductResponse)
async def scrape_product(payload: ProductCreateRequest, _: dict = Depends(get_current_user)):
    db = get_database()
    product_id = f"{payload.brand.strip().lower()}::{payload.model.strip().lower()}::{payload.variant_name.strip().lower()}"
    existing = await db.products.find_one({"_id": product_id})

    # Prefer existing rows mapped by platform URLs to avoid creating duplicates
    # when variant naming changes over time.
    if not existing:
        url_matchers = []
        if payload.amazon_url:
            url_matchers.append({"amazon_url": payload.amazon_url})
        if payload.flipkart_url:
            url_matchers.append({"flipkart_url": payload.flipkart_url})
        if payload.croma_url:
            url_matchers.append({"croma_url": payload.croma_url})

        if url_matchers:
            matched = await db.products.find_one({"$or": url_matchers})
            if matched:
                existing = matched
                product_id = str(matched.get("_id"))

    if existing and _is_cache_fresh(existing, payload.force_refresh):
        return _normalize_doc(existing)

    amazon, flipkart, croma = await asyncio.gather(
        asyncio.to_thread(scrape_single_platform, "amazon", payload.amazon_url or ""),
        asyncio.to_thread(scrape_single_platform, "flipkart", payload.flipkart_url or ""),
        asyncio.to_thread(scrape_single_platform, "croma", payload.croma_url or ""),
    )

    existing_prices = dict((existing or {}).get("prices") or {})

    prices = {
        "amazon": _resolved_price(amazon.get("price"), existing_prices.get("amazon")),
        "flipkart": _resolved_price(flipkart.get("price"), existing_prices.get("flipkart")),
        "croma": _resolved_price(croma.get("price"), existing_prices.get("croma")),
    }
    prices = _sanitize_prices(payload.category, prices)

    missing_platforms = [platform for platform, value in prices.items() if value is None]
    if missing_platforms:
        seed = " ".join(
            [
                str(payload.brand or "").strip(),
                str(payload.model or "").strip(),
                str(payload.variant_name or "").strip(),
            ]
        )
        seed = " ".join(seed.split())[:120]

        hits = await asyncio.gather(*[_safe_query_price(platform, seed) for platform in missing_platforms])
        query_hits = dict(zip(missing_platforms, hits))

        if prices["amazon"] is None:
            prices["amazon"] = (query_hits.get("amazon") or {}).get("price")
        if prices["flipkart"] is None:
            prices["flipkart"] = (query_hits.get("flipkart") or {}).get("price")
        if prices["croma"] is None:
            prices["croma"] = (query_hits.get("croma") or {}).get("price")
        prices = _sanitize_prices(payload.category, prices)

        if "amazon" in query_hits:
            amazon = _merge_scrape(amazon, query_hits["amazon"])
        if "flipkart" in query_hits:
            flipkart = _merge_scrape(flipkart, query_hits["flipkart"])
        if "croma" in query_hits:
            croma = _merge_scrape(croma, query_hits["croma"])

    best_price, best_platform = choose_best(prices)

    scraped_title = amazon.get("title") or flipkart.get("title") or croma.get("title")
    title = _prefer_variant_name(scraped_title, payload.variant_name)
    image_url = amazon.get("image_url") or flipkart.get("image_url") or croma.get("image_url")

    specs = {}
    for source in (amazon, flipkart, croma):
        for k, v in (source.get("specifications") or {}).items():
            if k not in specs and v:
                specs[k] = v

    doc = {
        "_id": product_id,
        "category": payload.category,
        "brand": payload.brand,
        "model": payload.model,
        "variant_name": title,
        "amazon_url": payload.amazon_url,
        "flipkart_url": payload.flipkart_url,
        "croma_url": payload.croma_url,
        "prices": prices,
        "image_url": image_url,
        "best_price": best_price,
        "best_platform": best_platform,
        "specifications": specs,
        "last_updated": now_utc(),
    }

    await db.products.update_one({"_id": product_id}, {"$set": doc}, upsert=True)
    return _normalize_doc(doc)


@router.post("/update-prices")
async def update_prices(payload: UpdatePricesRequest, _: dict = Depends(get_current_user)):
    db = get_database()
    docs = await db.products.find({}).to_list(length=payload.max_products)
    updated = 0
    skipped_fresh = 0
    failed = 0
    timed_out = 0
    last_error: Optional[str] = None
    started = now_utc()
    stopped_early = False

    for doc in docs:
        elapsed = (now_utc() - started).total_seconds()
        if elapsed >= payload.stop_after_seconds:
            stopped_early = True
            break

        if _is_cache_fresh(doc, payload.force_refresh):
            skipped_fresh += 1
            continue

        try:
            await asyncio.wait_for(_refresh_product_doc(db, doc), timeout=PER_PRODUCT_TIMEOUT_SECONDS)
            updated += 1
        except asyncio.TimeoutError:
            timed_out += 1
            last_error = "Per-product refresh timeout"
        except Exception as exc:
            failed += 1
            last_error = str(exc)

    return {
        "updated": updated,
        "skipped_fresh": skipped_fresh,
        "failed": failed,
        "timed_out": timed_out,
        "processed": updated + skipped_fresh + failed + timed_out,
        "total_candidates": len(docs),
        "stopped_early": stopped_early,
        "max_products": payload.max_products,
        "stop_after_seconds": payload.stop_after_seconds,
        "last_error": last_error,
    }


@router.post("/update-prices-quick")
async def update_prices_quick(
    background_tasks: BackgroundTasks,
    payload: UpdatePricesRequest,
    limit: int = Query(default=25, ge=1, le=200),
    _: dict = Depends(get_current_user),
):
    job_id = str(uuid4())
    _REFRESH_JOBS[job_id] = {
        "status": "queued",
        "limit": limit,
        "force_refresh": payload.force_refresh,
        "created_at": now_utc(),
    }
    background_tasks.add_task(_run_quick_refresh_job, job_id, payload.force_refresh, limit)

    return {
        "job_id": job_id,
        "status": "queued",
        "limit": limit,
    }


@router.get("/update-prices-quick/{job_id}")
async def get_update_prices_quick_job(job_id: str, _: dict = Depends(get_current_user)):
    job = _REFRESH_JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


def _to_csv_export_url(sheet_url: str) -> str:
    # Supports URLs like /edit?gid=0#gid=0
    if "/export?" in sheet_url:
        return sheet_url
    if "/edit" in sheet_url:
        base = sheet_url.split("/edit")[0]
        gid = "0"
        if "gid=" in sheet_url:
            gid = sheet_url.split("gid=")[-1].split("#")[0]
        return f"{base}/export?format=csv&gid={gid}"
    return sheet_url


@router.post("/import-products-sheet")
async def import_products_sheet(payload: ImportSheetRequest, _: dict = Depends(get_current_user)):
    csv_url = _to_csv_export_url(payload.sheet_url)
    res = requests.get(csv_url, timeout=20)
    res.raise_for_status()

    db = get_database()
    text = res.text
    reader = csv.DictReader(io.StringIO(text))

    imported = 0
    for row in reader:
        category = (row.get("category") or "phones").strip()
        brand = (row.get("brand") or "").strip()
        model = (row.get("model") or "").strip()
        variant_name = (row.get("variant_name") or model).strip()
        if not (brand and model and variant_name):
            continue

        req = ProductCreateRequest(
            category=category,
            brand=brand,
            model=model,
            variant_name=variant_name,
            amazon_url=(row.get("amazon_url") or "").strip() or None,
            flipkart_url=(row.get("flipkart_url") or "").strip() or None,
            croma_url=(row.get("croma_url") or "").strip() or None,
            force_refresh=payload.force_refresh,
        )
        await scrape_product(req, _)
        imported += 1

    return {"imported": imported}
