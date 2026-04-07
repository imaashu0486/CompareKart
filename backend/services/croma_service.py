"""
Croma India direct scraper using BeautifulSoup.
Fetches product data from croma.com search results.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode, quote_plus
import json
import re
from utils.scraper_utils import get_session_with_retries, get_headers, clean_price

logger = logging.getLogger(__name__)

CROMA_BASE_URL = "https://www.croma.com"
CROMA_SEARCH_URL = f"{CROMA_BASE_URL}/search"
CROMA_SEARCH_B_URL = f"{CROMA_BASE_URL}/searchB"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class CromaService:
    """
    Scrapes products from Croma India.
    Handles pagination and product attribute extraction.
    """

    def __init__(self) -> None:
        self.session = get_session_with_retries(retries=1, backoff_factor=0.2)

    def _request_headers(self) -> Dict[str, str]:
        headers = get_headers()
        headers.update(
            {
                "Host": "www.croma.com",
                "Referer": "https://www.croma.com/",
                "DNT": "1",
            }
        )
        return headers

    def search_products(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Croma for products.

        Args:
            query: Product search query
            max_results: Maximum number of results

        Returns:
            List of product dicts with: title, price, url, image_url, platform
        """
        try:
            products = []

            # Build search URL
            search_url = f"{CROMA_SEARCH_B_URL}?{urlencode({'text': query})}"
            logger.debug(f"Fetching Croma: {search_url}")

            soup = self._fetch_search_soup(search_url)
            if soup is None:
                logger.warning("Croma request fetch failed; trying Selenium fallback")
                soup = self._fetch_search_soup_selenium(search_url)

            if soup is None:
                return []

            if soup is None:
                return []

            # Find product containers on Croma
            items = soup.find_all("li", {"class": "product-item"})

            if not items:
                items = soup.find_all("div", {"class": "productCardImg"})

            if not items:
                items = soup.find_all("div", {"class": "productGrid"})

            if not items:
                items = soup.select("div[data-testid='product-card']")

            if not items:
                items = soup.select("a[href*='/'][title]")

            logger.debug(f"Found {len(items)} items on Croma")

            for item in items:
                if len(products) >= max_results:
                    break

                try:
                    product = self._extract_product_data(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error extracting product from Croma: {e}")
                    continue

            # Fallback parser for dynamic pages
            if not products:
                products = self._extract_from_json_ld(soup)

            if not products:
                products = self._extract_with_selenium_dom(search_url, max_results)

            if not products:
                products = self._extract_with_selenium_api(query, max_results)

            logger.info(f"Successfully scraped {len(products)} products from Croma")
            return products[:max_results]

        except Exception as e:
            logger.error(f"Croma scraping error: {e}")
            return []

    def _fetch_search_soup(self, search_url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse Croma search page via HTTP requests."""
        try:
            # Warmup request to set bot-protection cookies where possible
            self.session.get(
                CROMA_BASE_URL,
                headers=self._request_headers(),
                timeout=3,
            )

            response = self.session.get(
                search_url,
                headers=self._request_headers(),
                timeout=5,
            )
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            logger.warning(f"Croma request fetch failed: {e}")
            return None

    def _fetch_search_soup_selenium(self, search_url: str) -> Optional[BeautifulSoup]:
        """Fetch Croma search page using Selenium fallback."""
        try:
            from selenium.webdriver.common.by import By
            from utils.selenium_driver import get_selenium_driver

            driver = get_selenium_driver()
            page_source = driver.get_page_source(
                search_url,
                wait_for_element=(By.CSS_SELECTOR, "li.product-item, div[data-testid='product-card']"),
                timeout=10,
            )
            if not page_source:
                return None
            return BeautifulSoup(page_source, "html.parser")
        except Exception as e:
            logger.warning(f"Croma Selenium fallback failed: {e}")
            return None

    def _extract_with_selenium_dom(self, search_url: str, max_results: int) -> List[Dict[str, Any]]:
        """Extract Croma products directly from live browser DOM."""
        try:
            from utils.selenium_driver import get_selenium_driver

            driver = get_selenium_driver()
            driver.get_page_source(search_url, timeout=12)
            wd = driver.get_driver()

            rows = wd.execute_script(
                """
                const links = Array.from(document.querySelectorAll('a[href]'));
                const out = [];

                for (const a of links) {
                    const href = a.getAttribute('href') || '';
                    if (!href) continue;

                    // Croma product paths vary, keep broader but still product-oriented
                    const productLike = href.includes('/p/') || href.includes('/buy-') || href.includes('/mobile-') || href.includes('/product-');
                    if (!productLike) continue;

                    const card = a.closest('li, div, article, section') || a;
                    const cardText = (card.innerText || '').replace(/\s+/g, ' ').trim();

                    const title = (a.getAttribute('title') || a.textContent || '').replace(/\s+/g, ' ').trim() || cardText.slice(0, 140);
                    const priceMatch = cardText.match(/₹\s*[0-9,]+/);
                    const ratingMatch = cardText.match(/\b([0-4](?:\.[0-9])?|5(?:\.0)?)\b/);
                    const img = card.querySelector('img');

                    if (title && priceMatch) {
                        out.push({
                            href,
                            title,
                            priceText: priceMatch[0],
                            ratingText: ratingMatch ? ratingMatch[1] : '',
                            image: img ? (img.getAttribute('src') || img.getAttribute('data-src') || '') : ''
                        });
                    }
                }

                return out;
                """
            )

            products: List[Dict[str, Any]] = []
            seen: set[str] = set()

            for row in rows or []:
                if len(products) >= max_results:
                    break

                href = (row.get("href") or "").strip()
                title = (row.get("title") or "").strip()
                price = clean_price((row.get("priceText") or "").strip())

                if not href or not title or not price:
                    continue

                url = f"{CROMA_BASE_URL}{href}" if href.startswith("/") else href
                if url in seen:
                    continue
                seen.add(url)

                rating = None
                rating_text = (row.get("ratingText") or "").strip()
                if rating_text:
                    try:
                        rating = float(rating_text)
                    except Exception:
                        rating = None

                products.append(
                    {
                        "title": title,
                        "price": price,
                        "url": url,
                        "image_url": row.get("image") or None,
                        "rating": rating,
                        "platform": "Croma",
                        "source": "croma.com",
                    }
                )

            return products
        except Exception as e:
            logger.warning(f"Croma Selenium DOM extraction failed: {e}")
            return []

    def _extract_with_selenium_api(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """Use Croma internal search API via Selenium-acquired browser session context."""
        try:
            from utils.selenium_driver import get_selenium_driver

            driver = get_selenium_driver()
            search_url = f"{CROMA_SEARCH_B_URL}?{urlencode({'text': query})}"
            driver.get_page_source(search_url, timeout=12)
            wd = driver.get_driver()

            # First try browser-context fetch so request carries real browser
            # context/cookies and avoids direct client blocking.
            browser_products = self._extract_with_selenium_browser_fetch(wd, query, max_results)
            if browser_products:
                return browser_products[:max_results]

            api_url = (
                f"https://api.croma.com/searchservices/v1/search?currentPage=0&query="
                f"{quote_plus(query)}:relevance&fields=FULL&channel=WEB&channelCode=null&spellOpt=DEFAULT"
            )

            cookies = {c["name"]: c["value"] for c in wd.get_cookies()}
            response = requests.get(
                api_url,
                headers={
                    "User-Agent": get_headers().get("User-Agent", "Mozilla/5.0"),
                    "Accept": "application/json,text/plain,*/*",
                    "Referer": search_url,
                    "Origin": CROMA_BASE_URL,
                },
                cookies=cookies,
                timeout=10,
            )

            if response.status_code != 200:
                return []

            data = response.json()
            products = self._extract_products_from_api_payload(data)
            return products[:max_results]
        except Exception as e:
            logger.warning(f"Croma Selenium API extraction failed: {e}")
            return []

    def _extract_with_selenium_browser_fetch(
        self, wd: Any, query: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Fetch Croma API from inside browser context using window.fetch."""
        try:
            endpoint_urls = [
                f"/searchservices/v1/search?currentPage=0&query={quote_plus(query)}:relevance&fields=FULL&channel=WEB&channelCode=null&spellOpt=DEFAULT",
                f"/api/searchservices/v1/search?currentPage=0&query={quote_plus(query)}:relevance&fields=FULL&channel=WEB&channelCode=null&spellOpt=DEFAULT",
                f"https://api.croma.com/searchservices/v1/search?currentPage=0&query={quote_plus(query)}:relevance&fields=FULL&channel=WEB&channelCode=null&spellOpt=DEFAULT",
            ]

            js_fetch = """
                const done = arguments[arguments.length - 1];
                const apiUrl = arguments[0];

                fetch(apiUrl, {
                    method: 'GET',
                    credentials: 'include',
                    headers: {
                        'Accept': 'application/json,text/plain,*/*'
                    }
                })
                .then(async (response) => {
                    const text = await response.text();
                    done({ ok: response.ok, status: response.status, text });
                })
                .catch((error) => {
                    done({ ok: false, status: 0, text: String(error) });
                });
            """

            for endpoint in endpoint_urls:
                try:
                    result = wd.execute_async_script(js_fetch, endpoint)
                except Exception as fetch_err:
                    logger.debug(f"Croma browser fetch script failed for {endpoint}: {fetch_err}")
                    continue

                if not isinstance(result, dict):
                    continue

                if not result.get("ok"):
                    logger.debug(
                        f"Croma browser fetch failed for {endpoint}: status={result.get('status')}"
                    )
                    continue

                text = result.get("text") or ""
                if not text:
                    continue

                try:
                    data = json.loads(text)
                except Exception:
                    logger.debug(f"Croma browser fetch returned non-JSON payload for {endpoint}")
                    continue

                products = self._extract_products_from_api_payload(data)
                if products:
                    logger.info(
                        f"Croma browser-fetch API extraction succeeded via {endpoint} with {len(products)} products"
                    )
                    return products[:max_results]

            return []

        except Exception as e:
            logger.warning(f"Croma browser fetch extraction failed: {e}")
            return []

    def _extract_products_from_api_payload(self, data: Any) -> List[Dict[str, Any]]:
        """Recursively extract product-like objects from Croma API payload."""
        found: List[Dict[str, Any]] = []

        def to_price(value: Any) -> Optional[float]:
            if value is None:
                return None
            if isinstance(value, (int, float)):
                return float(value)
            return clean_price(str(value))

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                name = node.get("name") or node.get("title")
                url = node.get("url") or node.get("productUrl") or node.get("pdpUrl")

                price = None
                if "price" in node:
                    price = to_price(node.get("price"))
                if not price and isinstance(node.get("price"), dict):
                    price_obj = node.get("price")
                    price = (
                        to_price(price_obj.get("value"))
                        or to_price(price_obj.get("formattedValue"))
                        or to_price(price_obj.get("mrp"))
                    )
                if not price:
                    price = (
                        to_price(node.get("salePrice"))
                        or to_price(node.get("discountedPrice"))
                        or to_price(node.get("mrp"))
                    )

                image = node.get("image") or node.get("imageUrl") or node.get("thumbnail")
                if isinstance(image, list):
                    image = image[0] if image else None

                rating = None
                for key in ["rating", "averageRating", "ratingValue"]:
                    if node.get(key) is not None:
                        try:
                            rating = float(node.get(key))
                            break
                        except Exception:
                            pass

                if name and url and price:
                    url_str = str(url)
                    if url_str.startswith("/"):
                        url_str = f"{CROMA_BASE_URL}{url_str}"

                    found.append(
                        {
                            "title": str(name).strip(),
                            "price": float(price),
                            "url": url_str,
                            "image_url": image,
                            "rating": rating,
                            "platform": "Croma",
                            "source": "croma.com",
                        }
                    )

                for value in node.values():
                    walk(value)

            elif isinstance(node, list):
                for item in node:
                    walk(item)

        walk(data)

        dedup: Dict[str, Dict[str, Any]] = {}
        for item in found:
            dedup[item["url"]] = item
        return list(dedup.values())

    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract products from JSON-LD scripts when CSS selectors fail."""
        products: List[Dict[str, Any]] = []
        scripts = soup.find_all("script", {"type": "application/ld+json"})

        for script in scripts:
            raw = script.string or script.get_text(strip=True)
            if not raw:
                continue

            try:
                data = json.loads(raw)
            except Exception:
                continue

            candidates = data if isinstance(data, list) else [data]
            for candidate in candidates:
                products.extend(self._parse_json_ld_candidate(candidate))

        dedup: Dict[str, Dict[str, Any]] = {}
        for p in products:
            dedup[p["url"]] = p
        return list(dedup.values())

    def _parse_json_ld_candidate(self, data: Any) -> List[Dict[str, Any]]:
        """Parse a single JSON-LD node for product records."""
        found: List[Dict[str, Any]] = []
        if isinstance(data, dict):
            if str(data.get("@type", "")).lower() == "product":
                title = (data.get("name") or "").strip()
                url = (data.get("url") or "").strip()
                image_url = data.get("image")
                if isinstance(image_url, list):
                    image_url = image_url[0] if image_url else None

                offers = data.get("offers") or {}
                if isinstance(offers, list):
                    offers = offers[0] if offers else {}
                price = clean_price(str(offers.get("price", "")))

                rating = None
                agg = data.get("aggregateRating") or {}
                if isinstance(agg, dict):
                    try:
                        rating = float(agg.get("ratingValue")) if agg.get("ratingValue") else None
                    except Exception:
                        rating = None

                if title and price and url:
                    if url.startswith("/"):
                        url = f"{CROMA_BASE_URL}{url}"
                    found.append(
                        {
                            "title": title,
                            "price": price,
                            "url": url,
                            "image_url": image_url,
                            "rating": rating,
                            "platform": "Croma",
                            "source": "croma.com",
                        }
                    )

            for value in data.values():
                found.extend(self._parse_json_ld_candidate(value))
        elif isinstance(data, list):
            for entry in data:
                found.extend(self._parse_json_ld_candidate(entry))

        return found

    def _extract_product_data(self, item: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Extract product data from Croma search result item.

        Args:
            item: BeautifulSoup element representing a product

        Returns:
            Product dict or None if extraction failed
        """
        try:
            # Title
            title_elem = (
                item.find("span", {"class": "productCardText"})
                or item.select_one("h3")
                or item.select_one("a[title]")
            )
            if not title_elem:
                return None

            title = title_elem.get("title") if hasattr(title_elem, "get") else None
            if not title:
                title = title_elem.get_text(strip=True)
            if not title:
                return None

            # Price (in INR)
            price_elem = item.find("span", {"class": "amount"}) or item.select_one("span[class*='amount']")
            price = clean_price(price_elem.get_text(strip=True)) if price_elem else None
            if not price:
                text_blob = item.get_text(" ", strip=True)
                price_match = re.search(r"₹\s*([\d,]{4,})", text_blob)
                if price_match:
                    price = clean_price(f"₹{price_match.group(1)}")

            # Product URL
            link_elem = (
                item.find("a", {"class": "productCard"})
                or item.select_one("a[href*='/']")
            )
            url = None
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                url = f"{CROMA_BASE_URL}{href}" if href.startswith("/") else href

            # Image URL
            image_elem = item.find("img")
            image_url = None
            if image_elem:
                image_url = image_elem.get("src") or image_elem.get("data-src")

            # Rating
            rating_elem = item.find("span", {"class": "rating"})
            rating = None
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                try:
                    rating = float(rating_text.split()[0])
                except:
                    rating = None

            if not title or not price or not url:
                return None

            return {
                "title": title,
                "price": price,
                "url": url,
                "image_url": image_url,
                "rating": rating,
                "platform": "Croma",
                "source": "croma.com",
            }

        except Exception as e:
            logger.debug(f"Error extracting product data: {e}")
            return None
