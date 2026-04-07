import json
import random
import re
import time
from datetime import datetime, timezone
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from rapidfuzz import fuzz
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.util.retry import Retry

CACHE_TTL_SECONDS = 1800
_SCRAPE_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
_HTTP_SESSION: Optional[requests.Session] = None


def _parse_price(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    cleaned = str(value).replace("₹", "").replace(",", "").strip()
    cleaned = re.sub(r"\s+", "", cleaned)
    if not cleaned:
        return None

    # If decimal format is present, keep rupee part only.
    if "." in cleaned:
        cleaned = cleaned.split(".", 1)[0]

    cleaned = re.sub(r"[^\d]", "", cleaned)
    if not cleaned:
        return None

    try:
        return int(cleaned)
    except ValueError:
        return None


def _pick_primary_price(candidates: list[int]) -> Optional[int]:
    values = [int(v) for v in candidates if isinstance(v, (int, float)) and int(v) > 0]
    if not values:
        return None

    top = max(values)
    # Keep realistic candidates near the top range; this drops low EMI/exchange values.
    near_top = [v for v in values if v >= int(top * 0.5)]
    if near_top:
        return min(near_top)
    return min(values)

def _is_noise_price_text(text: Optional[str]) -> bool:
    if not text:
        return False
    lowered = str(text).lower()
    noise_tokens = [
        "emi",
        "/month",
        "per month",
        "month",
        "exchange",
        "cashback",
        "bank offer",
        "discount",
        "save",
        "off",
        "starting",
        "starts",
        "from",
    ]
    return any(token in lowered for token in noise_tokens)

def _normalize_platform_price(platform: str, price: Optional[int]) -> Optional[int]:
    if price is None:
        return None
    # Croma pages often surface EMI/offer snippets first (e.g. ₹139/month).
    # Treat very small values as invalid product prices.
    if platform == "croma" and int(price) < 1000:
        return None
    return int(price)
def _get_http_session() -> requests.Session:
    global _HTTP_SESSION
    if _HTTP_SESSION is not None:
        return _HTTP_SESSION

    session = requests.Session()
    retry = Retry(
        total=2,
        connect=2,
        read=2,
        backoff_factor=0.4,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-IN,en;q=0.9",
        }
    )
    _HTTP_SESSION = session
    return _HTTP_SESSION


def _get_cached(cache_key: str) -> Optional[Dict[str, Any]]:
    row = _SCRAPE_CACHE.get(cache_key)
    if not row:
        return None
    timestamp, data = row
    if time.time() - timestamp > CACHE_TTL_SECONDS:
        _SCRAPE_CACHE.pop(cache_key, None)
        return None
    return data


def _set_cached(cache_key: str, data: Dict[str, Any]) -> None:
    _SCRAPE_CACHE[cache_key] = (time.time(), data)


def _fetch_html(url: str) -> Optional[str]:
    try:
        session = _get_http_session()
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception:
        return None


def _title_from_url(url: str, platform: Optional[str] = None) -> Optional[str]:
    try:
        parts = [part for part in url.split("?")[0].rstrip("/").split("/") if part]
        slug = parts[-1] if parts else ""

        if platform == "flipkart" or platform == "croma":
            for part in reversed(parts[:-1]):
                if part.lower() == "p":
                    continue
                if re.fullmatch(r"itm[a-z0-9]+", part, flags=re.I):
                    continue
                if re.fullmatch(r"\d+", part):
                    continue
                if any(ch.isalpha() for ch in part) and "-" in part:
                    slug = part
                    break

        if slug.startswith("itm") and len(slug) > 10 and "-" not in slug:
            return None
        if slug.isdigit():
            return None

        slug = slug.replace("-", " ").replace("_", " ").strip()
        if not slug or len(slug) < 4:
            return None
        return re.sub(r"\s+", " ", slug).title()
    except Exception:
        return None


def _clean_title(title: Optional[str]) -> Optional[str]:
    if not title:
        return None
    normalized = re.sub(r"\s+", " ", str(title)).strip()
    lowered = normalized.lower()
    blocked_tokens = ["access denied", "captcha", "robot check", "temporarily unavailable", "forbidden", "not found"]
    if any(token in lowered for token in blocked_tokens):
        return None
    normalized = re.sub(r"\s*\|\s*.*$", "", normalized)
    normalized = re.sub(r"\s*-\s*(croma|amazon|flipkart)\s*$", "", normalized, flags=re.I)
    normalized = re.sub(r"\bGb\b", "GB", normalized)
    normalized = re.sub(r"\bTb\b", "TB", normalized)
    normalized = re.sub(r"\bMah\b", "mAh", normalized)
    normalized = re.sub(r"\bIphone\b", "iPhone", normalized, flags=re.I)
    normalized = re.sub(r"\bIpad\b", "iPad", normalized, flags=re.I)
    normalized = re.sub(r"\bIwatch\b", "iWatch", normalized, flags=re.I)
    return normalized


def _extract_meta_content(soup: BeautifulSoup, names: list[str], attr: str = "content") -> Optional[str]:
    for name in names:
        selectors = [
            f"meta[property='{name}']",
            f"meta[name='{name}']",
            f"meta[itemprop='{name}']",
        ]
        for selector in selectors:
            value = _safe_attr_soup(soup, selector, attr)
            if value:
                return value
    return None


def _extract_title_from_json_ld(soup: BeautifulSoup) -> Optional[str]:
    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue
        try:
            parsed = json.loads(raw)
        except Exception:
            continue
        for obj in _walk_json_nodes(parsed):
            title = obj.get("name")
            if isinstance(title, str) and title.strip():
                return title.strip()
    return None


def _fallback_query_from_url(url: str, platform: Optional[str] = None) -> Optional[str]:
    title = _title_from_url(url, platform)
    if not title:
        return None

    cleaned = re.sub(r"\b(p|itm[a-z0-9]+|buy)\b", " ", title, flags=re.I)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or None


def _candidate_croma_queries(seed: str) -> list[str]:
    if not seed:
        return []

    normalized = re.sub(r"\s+", " ", seed).strip()
    colors = r"(?:black|white|blue|silver|gold|green|red|pink|purple|graphite|starlight|midnight|yellow|orange|beige|cream|ultramarine|teal|coral|lavender)"
    storage = r"(?:\d{2,4}\s?(?:gb|tb))"

    def strip_pattern(text: str, pattern: str) -> str:
        return re.sub(pattern, "", text, flags=re.I)

    variants = []
    variants.append(normalized)
    variants.append(strip_pattern(normalized, r"^Apple\s+"))
    variants.append(strip_pattern(normalized, rf"\s+{colors}\b"))
    variants.append(strip_pattern(normalized, rf"\s+{storage}\b"))
    variants.append(strip_pattern(normalized, rf"\s+{colors}\b\s+{storage}\b"))
    variants.append(strip_pattern(normalized, rf"\s+{storage}\b\s+{colors}\b"))

    compact = re.sub(r"\b(?:pro\s*max|pro|plus|ultra|max|mini|fe|lite|neo|gt)\b", "", normalized, flags=re.I)
    compact = re.sub(r"\s+", " ", compact).strip()

    variants.append(compact)

    base_words = compact.split()
    candidates: list[str] = []

    # Prefer exact and slightly broader branded queries first.
    for variant in variants:
        if variant:
            candidates.append(variant)

    if len(base_words) >= 4:
        candidates.append(" ".join(base_words[:4]))
    if len(base_words) >= 3:
        candidates.append(" ".join(base_words[:3]))
    if len(base_words) >= 2:
        candidates.append(" ".join(base_words[:2]))
    if base_words:
        candidates.append(base_words[0])

    # Deduplicate while preserving order.
    seen: set[str] = set()
    ordered: list[str] = []
    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if len(candidate) < 2 or candidate.lower() in seen:
            continue
        seen.add(candidate.lower())
        ordered.append(candidate)
    return ordered


def _choose_best_search_result(query: str, results: list[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not results:
        return None

    query_norm = normalize_query = re.sub(r"\s+", " ", query.lower()).strip()
    best_item = None
    best_score = -1

    for item in results:
        title = str(item.get("title") or "").strip()
        if not title:
            continue
        title_norm = re.sub(r"\s+", " ", title.lower()).strip()
        score = fuzz.token_set_ratio(query_norm, title_norm)
        if query_norm and query_norm in title_norm:
            score += 20
        if item.get("price") is not None:
            score += 15
        if item.get("image_url"):
            score += 5
        if score > best_score:
            best_score = score
            best_item = item

    return best_item


def _search_croma_fallback(query: str, max_results: int = 5) -> Optional[Dict[str, Any]]:
    if not query:
        return None

    try:
        from services.croma_service import CromaService

        service = CromaService()
        for candidate in _candidate_croma_queries(query):
            results = service.search_products(candidate, max_results=max_results)
            best = _choose_best_search_result(candidate, results)
            if best:
                return best
    except Exception:
        return None

    return None


def _search_platform_fallback(platform: str, query: str, max_results: int = 5) -> Optional[Dict[str, Any]]:
    if not query:
        return None

    try:
        if platform == "amazon":
            from services.amazon_service import AmazonService

            service = AmazonService()
            for candidate in _candidate_croma_queries(query):
                results = service.search_products(candidate, max_results=max_results)
                best = _choose_best_search_result(candidate, results)
                if best:
                    return best
            return None

        if platform == "flipkart":
            from services.flipkart_service import FlipkartService

            service = FlipkartService()
            for candidate in _candidate_croma_queries(query):
                results = service.search_products(candidate, max_results=max_results)
                best = _choose_best_search_result(candidate, results)
                if best:
                    return best
            return None

        return _search_croma_fallback(query, max_results=max_results)
    except Exception:
        return None


def _apply_platform_search_fallback(platform: str, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("price") is not None and data.get("title") and data.get("image_url"):
        return data

    fallback_query = _clean_title(data.get("title")) or _fallback_query_from_url(url, platform)
    if not fallback_query:
        return data

    search_hit = _search_platform_fallback(platform, fallback_query)
    if not search_hit:
        return data

    data["title"] = data.get("title") or search_hit.get("title")
    data["price"] = data.get("price") if data.get("price") is not None else search_hit.get("price")
    data["image_url"] = data.get("image_url") or search_hit.get("image_url")
    return data


def _wait_any_price_element(driver: webdriver.Chrome, selectors: str, timeout: int = 10) -> None:
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selectors))
        )
    except Exception:
        pass


def _safe_text_soup(soup: BeautifulSoup, selector: str) -> Optional[str]:
    node = soup.select_one(selector)
    if not node:
        return None
    text = node.get_text(" ", strip=True)
    return text or None


def _safe_attr_soup(soup: BeautifulSoup, selector: str, attr: str) -> Optional[str]:
    node = soup.select_one(selector)
    if not node:
        return None
    value = node.get(attr)
    if isinstance(value, list):
        value = value[0] if value else None
    return str(value).strip() if value else None


def _extract_price_amazon_soup(soup: BeautifulSoup) -> Optional[int]:
    for node in soup.select(".a-price .a-offscreen"):
        price = _parse_price(node.get_text(" ", strip=True))
        if price:
            return price

    whole = soup.select_one("span.a-price-whole")
    fraction = soup.select_one("span.a-price-fraction")
    if whole:
        combo = f"{whole.get_text(strip=True)}.{fraction.get_text(strip=True) if fraction else '00'}"
        return _parse_price(combo)

    text_blob = soup.get_text(" ", strip=True)
    match = re.search(r"₹\s*([\d,]+(?:\.\d{1,2})?)", text_blob)
    return _parse_price(match.group(1)) if match else None


def _extract_price_flipkart_soup(soup: BeautifulSoup) -> Optional[int]:
    selectors = ["div._30jeq3", "div.Nx9bqj", "div[class*='Nx9bqj']"]
    candidates: list[int] = []
    for selector in selectors:
        for node in soup.select(selector):
            price = _parse_price(node.get_text(" ", strip=True))
            if price:
                candidates.append(price)

    picked = _pick_primary_price(candidates)
    if picked:
        return picked

    text_blob = soup.get_text(" ", strip=True)
    match = re.search(r"₹\s*([\d,]+(?:\.\d{1,2})?)", text_blob)
    return _parse_price(match.group(1)) if match else None


def _extract_price_croma_soup(soup: BeautifulSoup) -> Optional[int]:
    selectors = [
        "span.amount",
        "span[class*='amount']",
        "span[data-testid*='price']",
        "span[class*='selling']",
        "span[class*='price']",
        "div[class*='price']",
    ]
    candidates: list[int] = []
    for selector in selectors:
        for node in soup.select(selector):
            text = node.get_text(" ", strip=True)
            if _is_noise_price_text(text):
                continue
            price = _parse_price(text)
            if price and price >= 1000:
                candidates.append(price)

    picked = _pick_primary_price(candidates)
    if picked:
        return picked
    meta_price = _extract_meta_content(soup, ["product:price:amount", "price", "og:price:amount", "twitter:data1"])
    if meta_price:
        parsed = _parse_price(meta_price)
        if parsed and parsed >= 1000:
            return parsed

    text_blob = soup.get_text(" ", strip=True)
    matches = re.findall(r"₹\s*([\d,]{4,}(?:\.\d{1,2})?)", text_blob)
    parsed = [_parse_price(m) for m in matches]
    parsed = [int(v) for v in parsed if isinstance(v, int) and v >= 1000]
    return _pick_primary_price(parsed)


def _extract_generic_price_soup(soup: BeautifulSoup) -> Optional[int]:
    meta_price = _extract_meta_content(
        soup,
        [
            "product:price:amount",
            "og:price:amount",
            "twitter:data1",
            "price",
        ],
    )
    if meta_price:
        parsed = _parse_price(meta_price)
        if parsed:
            return parsed

    itemprop_price = _safe_attr_soup(soup, "[itemprop='price']", "content") or _safe_text_soup(soup, "[itemprop='price']")
    if itemprop_price:
        parsed = _parse_price(itemprop_price)
        if parsed:
            return parsed

    for script in soup.find_all("script"):
        script_text = script.string or script.get_text(" ", strip=True)
        if not script_text:
            continue
        m = re.search(r'"price"\s*:\s*"?([\d,]{3,}(?:\.\d{1,2})?)"?', script_text)
        if m:
            parsed = _parse_price(m.group(1))
            if parsed:
                return parsed

    text_blob = soup.get_text(" ", strip=True)
    m = re.search(r"(?:₹|Rs\.?|INR)\s*([\d,]{3,}(?:\.\d{1,2})?)", text_blob, flags=re.I)
    if m:
        return _parse_price(m.group(1))
    return None


def _extract_platform_bs(platform: str, soup: BeautifulSoup) -> Dict[str, Any]:
    if platform == "amazon":
        amazon_price = _extract_price_amazon_soup(soup) or _extract_generic_price_soup(soup)
        return {
            "title": _clean_title(
                _safe_text_soup(soup, "#productTitle")
                or _safe_text_soup(soup, "h1 span")
                or _extract_meta_content(soup, ["og:title", "twitter:title", "title"])
                or _extract_title_from_json_ld(soup)
            ),
            "price": amazon_price,
            "image_url": _safe_attr_soup(soup, "#landingImage", "src") or _safe_attr_soup(soup, "#imgTagWrapperId img", "src") or _extract_meta_content(soup, ["og:image", "twitter:image"]),
            "brand": _safe_text_soup(soup, "a#bylineInfo") or _extract_meta_content(soup, ["product:brand"]),
        }

    if platform == "flipkart":
        flipkart_price = _extract_price_flipkart_soup(soup) or _extract_generic_price_soup(soup)
        return {
            "title": _clean_title(
                _safe_text_soup(soup, "span.B_NuCI")
                or _safe_text_soup(soup, "h1 span")
                or _extract_meta_content(soup, ["og:title", "twitter:title", "title"])
                or _extract_title_from_json_ld(soup)
            ),
            "price": flipkart_price,
            "image_url": _safe_attr_soup(soup, "img._396cs4", "src") or _safe_attr_soup(soup, "img[loading='eager']", "src") or _extract_meta_content(soup, ["og:image", "twitter:image"]),
            "brand": _extract_meta_content(soup, ["product:brand", "og:brand"]),
        }

    croma_price = _extract_price_croma_soup(soup) or _extract_generic_price_soup(soup)
    croma_price = _normalize_platform_price("croma", croma_price)
    return {
        "title": _clean_title(
            _safe_text_soup(soup, "h1.product-title")
            or _safe_text_soup(soup, "h1")
            or _extract_meta_content(soup, ["og:title", "twitter:title", "title"])
            or _extract_title_from_json_ld(soup)
        ),
        "price": croma_price,
        "image_url": _safe_attr_soup(soup, "img.product-image", "src") or _extract_meta_content(soup, ["og:image", "twitter:image"]),
        "brand": _extract_meta_content(soup, ["product:brand", "og:brand"]),
    }


def _walk_json_nodes(node: Any):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_json_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_json_nodes(item)


def _extract_json_ld_product(soup: BeautifulSoup) -> Dict[str, Any]:
    best = {"title": None, "price": None, "image_url": None, "brand": None}

    scripts = soup.find_all("script", {"type": "application/ld+json"})
    for script in scripts:
        raw = script.string or script.get_text(strip=True)
        if not raw:
            continue

        try:
            parsed = json.loads(raw)
        except Exception:
            continue

        for obj in _walk_json_nodes(parsed):
            node_type = str(obj.get("@type", "")).lower()
            if node_type != "product" and "offers" not in obj:
                continue

            title = obj.get("name")
            image = obj.get("image")
            brand = obj.get("brand")
            offers = obj.get("offers") or {}

            if isinstance(image, list):
                image = image[0] if image else None

            if isinstance(brand, dict):
                brand = brand.get("name")

            if isinstance(offers, list):
                offers = offers[0] if offers else {}

            price = None
            if isinstance(offers, dict):
                price = _parse_price(str(offers.get("price") or offers.get("lowPrice") or ""))

            if not price:
                price = _parse_price(str(obj.get("price") or ""))

            candidate = {
                "title": str(title).strip() if title else None,
                "price": price,
                "image_url": str(image).strip() if image else None,
                "brand": str(brand).strip() if brand else None,
            }

            if candidate["title"] or candidate["price"] or candidate["image_url"]:
                # Prefer nodes with price present.
                if candidate["price"] is not None:
                    return candidate
                if not best["title"]:
                    best = candidate

    return best


def _extract_price_amazon(driver: webdriver.Chrome) -> Optional[int]:
    _wait_any_price_element(driver, ".a-price .a-offscreen, .a-price-whole, .a-price-fraction", timeout=10)

    try:
        offscreen = driver.find_elements(By.CSS_SELECTOR, ".a-price .a-offscreen")
        for element in offscreen:
            value = _parse_price(element.text or "")
            if value:
                return value
    except Exception:
        pass

    try:
        whole = driver.find_elements(By.CSS_SELECTOR, ".a-price-whole")
        fraction = driver.find_elements(By.CSS_SELECTOR, ".a-price-fraction")
        if whole:
            whole_text = whole[0].text or ""
            fraction_text = fraction[0].text if fraction else "00"
            value = _parse_price(f"{whole_text}.{fraction_text}")
            if value:
                return value
    except Exception:
        pass

    return None


def _extract_price_flipkart(driver: webdriver.Chrome) -> Optional[int]:
    _wait_any_price_element(driver, "div._30jeq3, div.Nx9bqj, div[class*='Nx9bqj']", timeout=10)
    selectors = ["div._30jeq3", "div.Nx9bqj", "div[class*='Nx9bqj']"]
    candidates: list[int] = []

    for selector in selectors:
        try:
            nodes = driver.find_elements(By.CSS_SELECTOR, selector)
            for node in nodes:
                value = _parse_price(node.text or "")
                if value:
                    candidates.append(value)
        except Exception:
            continue

    picked = _pick_primary_price(candidates)
    if picked:
        return picked

    try:
        text_blob = driver.execute_script("return document.body ? document.body.innerText : '';") or ""
        match = re.search(r"₹\s*([\d,]+(?:\.\d{1,2})?)", text_blob)
        if match:
            return _parse_price(match.group(1))
    except Exception:
        pass

    return None


def _extract_price_croma(driver: webdriver.Chrome) -> Optional[int]:
    _wait_any_price_element(driver, "span.amount, span[class*='amount'], span[data-testid*='price']", timeout=10)
    selectors = ["span.amount", "span[class*='amount']", "span[data-testid*='price']"]

    candidates: list[int] = []
    for selector in selectors:
        try:
            nodes = driver.find_elements(By.CSS_SELECTOR, selector)
            for node in nodes:
                raw = node.text or ""
                if _is_noise_price_text(raw):
                    continue
                value = _parse_price(raw)
                if value and value >= 1000:
                    candidates.append(value)
        except Exception:
            continue

    picked = _pick_primary_price(candidates)
    if picked:
        return picked
    try:
        text_blob = driver.execute_script("return document.body ? document.body.innerText : '';") or ""
        matches = re.findall(r"₹\s*([\d,]{4,}(?:\.\d{1,2})?)", text_blob)
        parsed = [_parse_price(m) for m in matches]
        parsed = [int(v) for v in parsed if isinstance(v, int) and v >= 1000]
        picked = _pick_primary_price(parsed)
        if picked:
            return picked
    except Exception:
        pass

    return None


def _create_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1366,768")
    options.page_load_strategy = "eager"
    return webdriver.Chrome(options=options)


def _safe_text(driver: webdriver.Chrome, selector_by: By, selector: str, timeout: int = 8) -> Optional[str]:
    try:
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((selector_by, selector)))
        return el.text.strip() if el.text else (el.get_attribute("content") or "").strip()
    except Exception:
        return None


def _safe_attr(driver: webdriver.Chrome, selector_by: By, selector: str, attr: str, timeout: int = 8) -> Optional[str]:
    try:
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((selector_by, selector)))
        value = el.get_attribute(attr)
        return value.strip() if value else None
    except Exception:
        return None


def _extract_specs_from_html(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    specs: Dict[str, Any] = {}

    # Keep only key highlights for consistency.
    text = soup.get_text(" ", strip=True).lower()
    patterns = {
        "battery": r"(\d{3,5}\s*mAh)",
        "ram": r"(\d{1,2}\s*gb\s*ram)",
        "storage": r"(\d{2,4}\s*gb\s*(?:storage|rom|internal)?)",
    }
    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            specs[key] = m.group(1)

    return specs


def _scrape_with_selenium(platform: str, url: str) -> Dict[str, Any]:
    driver = _create_driver()
    try:
        time.sleep(random.uniform(0.5, 1.2))
        driver.get(url)
        specs = _extract_specs_from_html(driver.page_source)

        if platform == "amazon":
            title = _safe_text(driver, By.CSS_SELECTOR, "#productTitle") or _safe_text(driver, By.CSS_SELECTOR, "h1 span")
            price = _extract_price_amazon(driver)
            image = _safe_attr(driver, By.CSS_SELECTOR, "#landingImage", "src")
        elif platform == "flipkart":
            title = _safe_text(driver, By.CSS_SELECTOR, "span.B_NuCI") or _safe_text(driver, By.CSS_SELECTOR, "h1 span")
            price = _extract_price_flipkart(driver)
            image = _safe_attr(driver, By.CSS_SELECTOR, "img._396cs4", "src") or _safe_attr(driver, By.CSS_SELECTOR, "meta[property='og:image']", "content")
        else:
            title = _safe_text(driver, By.CSS_SELECTOR, "h1.product-title") or _safe_text(driver, By.CSS_SELECTOR, "h1")
            price = _extract_price_croma(driver)
            image = _safe_attr(driver, By.CSS_SELECTOR, "img.product-image", "src") or _safe_attr(driver, By.CSS_SELECTOR, "meta[property='og:image']", "content")

        return {
            "title": title,
            "price": price,
            "image_url": image,
            "specifications": specs,
        }
    except Exception:
        return {
            "title": None,
            "price": None,
            "image_url": None,
            "specifications": {},
        }
    finally:
        driver.quit()


def scrape_single_platform(platform: str, url: str, allow_selenium: bool = True) -> Dict[str, Any]:
    if not url:
        return {"title": None, "price": None, "image_url": None, "specifications": {}}

    cache_key = f"{platform}|{url}|sel={1 if allow_selenium else 0}"
    cached = _get_cached(cache_key)
    if cached is not None:
        return cached

    # Primary strategy: requests + BeautifulSoup + JSON-LD.
    html = _fetch_html(url)
    if html:
        soup = BeautifulSoup(html, "html.parser")
        json_ld_data = _extract_json_ld_product(soup)
        bs_data = _extract_platform_bs(platform, soup)

        data = {
            "title": _clean_title(json_ld_data.get("title") or bs_data.get("title")),
            "price": json_ld_data.get("price") if json_ld_data.get("price") is not None else bs_data.get("price"),
            "image_url": json_ld_data.get("image_url") or bs_data.get("image_url") or _safe_attr_soup(soup, "img[src]", "src"),
            "specifications": _extract_specs_from_html(html),
        }
        data["price"] = _normalize_platform_price(platform, data.get("price"))

        # Selenium fallback only when enabled and critical fields are missing.
        if allow_selenium and (data["price"] is None or not data["title"]):
            fallback = _scrape_with_selenium(platform, url)
            data["title"] = data["title"] or fallback.get("title")
            data["price"] = data["price"] if data["price"] is not None else fallback.get("price")
            data["image_url"] = data["image_url"] or fallback.get("image_url")
            if not data["specifications"]:
                data["specifications"] = fallback.get("specifications") or {}
            data["price"] = _normalize_platform_price(platform, data.get("price"))

        data = _apply_platform_search_fallback(platform, url, data)

        data["title"] = _clean_title(data.get("title"))
        if not data["title"]:
            data["title"] = _title_from_url(url, platform)

        _set_cached(cache_key, data)
        return data

    # Fallback strategy: Selenium only when requests fails and fallback is enabled.
    if not allow_selenium:
        data = {"title": _title_from_url(url, platform), "price": None, "image_url": None, "specifications": {}}
        data = _apply_platform_search_fallback(platform, url, data)
        data["title"] = _clean_title(data.get("title")) or data.get("title")
        _set_cached(cache_key, data)
        return data

    data = _scrape_with_selenium(platform, url)
    data["price"] = _normalize_platform_price(platform, data.get("price"))
    data["title"] = _clean_title(data.get("title"))
    if not data.get("title"):
        data["title"] = _title_from_url(url, platform)
    data = _apply_platform_search_fallback(platform, url, data)
    data["title"] = _clean_title(data.get("title")) or data.get("title")
    _set_cached(cache_key, data)
    return data


def choose_best(prices: Dict[str, Optional[float]]) -> tuple[Optional[float], Optional[str]]:
    available = {
        k: float(v)
        for k, v in prices.items()
        if isinstance(v, (int, float)) and float(v) > 0
    }
    if not available:
        return None, None
    platform = min(available, key=available.get)
    return float(available[platform]), platform


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
