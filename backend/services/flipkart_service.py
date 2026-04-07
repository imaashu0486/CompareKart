"""
Flipkart India direct scraper using BeautifulSoup.
Fetches product data from flipkart.com search results.
"""

import logging
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
import json
import re
from utils.scraper_utils import get_session_with_retries, get_headers, clean_price

logger = logging.getLogger(__name__)

FLIPKART_BASE_URL = "https://www.flipkart.com"
FLIPKART_SEARCH_URL = f"{FLIPKART_BASE_URL}/search"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class FlipkartService:
    """
    Scrapes products from Flipkart India.
    Handles pagination and product attribute extraction.
    """

    def __init__(self) -> None:
        self.session = get_session_with_retries(retries=1, backoff_factor=0.2)

    def _request_headers(self) -> Dict[str, str]:
        headers = get_headers()
        headers.update(
            {
                "Host": "www.flipkart.com",
                "Referer": "https://www.flipkart.com/",
                "DNT": "1",
            }
        )
        return headers

    def search_products(
        self, query: str, max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search Flipkart for products.

        Args:
            query: Product search query
            max_results: Maximum number of results

        Returns:
            List of product dicts with: title, price, url, image_url, platform
        """
        try:
            products = []

            # Build search URL
            search_url = f"{FLIPKART_SEARCH_URL}?{urlencode({'q': query})}"
            logger.debug(f"Fetching Flipkart: {search_url}")

            soup = self._fetch_search_soup(search_url)
            if soup is None:
                logger.warning("Flipkart request fetch failed; trying Selenium fallback")
                soup = self._fetch_search_soup_selenium(search_url)

            if soup is None:
                return []

            if soup is None:
                return []

            # Find product containers on Flipkart
            items = soup.find_all("div", {"class": "_1AtVbE"})

            if not items:
                items = soup.find_all("div", {"class": "_2kHmtq"})

            if not items:
                items = soup.select("div[data-id]")

            if not items:
                items = soup.select("a[href*='/p/']")

            logger.debug(f"Found {len(items)} items on Flipkart")

            for item in items:
                if len(products) >= max_results:
                    break

                try:
                    product = self._extract_product_data(item)
                    if product:
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error extracting product from Flipkart: {e}")
                    continue

            # Fallback parser for heavily dynamic pages
            if not products:
                products = self._extract_from_json_ld(soup)

            if not products:
                products = self._extract_with_selenium_dom(search_url, max_results)

            logger.info(f"Successfully scraped {len(products)} products from Flipkart")
            return products[:max_results]

        except Exception as e:
            logger.error(f"Flipkart scraping error: {e}")
            return []

    def _fetch_search_soup(self, search_url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse Flipkart search page via HTTP requests."""
        try:
            # Warmup request to establish cookies/session
            self.session.get(
                FLIPKART_BASE_URL,
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
            logger.warning(f"Flipkart request fetch failed: {e}")
            return None

    def _fetch_search_soup_selenium(self, search_url: str) -> Optional[BeautifulSoup]:
        """Fetch Flipkart search page using Selenium fallback."""
        try:
            from selenium.webdriver.common.by import By
            from utils.selenium_driver import get_selenium_driver

            driver = get_selenium_driver()
            page_source = driver.get_page_source(
                search_url,
                wait_for_element=(By.CSS_SELECTOR, "a[href*='/p/'], div[data-id]"),
                timeout=10,
            )
            if not page_source:
                return None
            return BeautifulSoup(page_source, "html.parser")
        except Exception as e:
            logger.warning(f"Flipkart Selenium fallback failed: {e}")
            return None

    def _extract_from_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract products from JSON-LD scripts when card selectors fail."""
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
            # Product node
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
                        url = f"{FLIPKART_BASE_URL}{url}"
                    found.append(
                        {
                            "title": title,
                            "price": price,
                            "url": url,
                            "image_url": image_url,
                            "rating": rating,
                            "platform": "Flipkart",
                            "source": "flipkart.com",
                        }
                    )

            # Recurse nested structures
            for value in data.values():
                found.extend(self._parse_json_ld_candidate(value))
        elif isinstance(data, list):
            for entry in data:
                found.extend(self._parse_json_ld_candidate(entry))

        return found

    def _extract_with_selenium_dom(self, search_url: str, max_results: int) -> List[Dict[str, Any]]:
        """Extract products directly from live browser DOM via Selenium JS execution."""
        try:
            from utils.selenium_driver import get_selenium_driver

            driver = get_selenium_driver()
            # ensure page loaded in Selenium session
            driver.get_page_source(search_url, timeout=10)
            wd = driver.get_driver()

            rows = wd.execute_script(
                """
                const cards = Array.from(document.querySelectorAll('div[data-id]'));
                const out = [];
                for (const card of cards) {
                    const link = card.querySelector("a[href*='/p/']");
                    const titleEl = card.querySelector("div.KzDlHZ, a[title], div._4rR01T, a.IRpwTa");
                    const priceEl = card.querySelector("div.Nx9bqj, div._30jeq3, div.hZ3P6w");
                    const ratingEl = card.querySelector("div.XQDdHH, div._3LWZlK");
                    const imageEl = card.querySelector("img");

                    const text = (card.innerText || '').replace(/\s+/g, ' ').trim();
                    const fallbackPrice = text.match(/₹\s*[0-9,]+/);

                    const href = link ? (link.getAttribute('href') || '') : '';
                    let title = titleEl ? ((titleEl.getAttribute('title') || titleEl.textContent || '').trim()) : '';
                    if (!title && link) {
                        title = (link.textContent || '').replace(/\s+/g, ' ').trim();
                    }
                    if (title) {
                        title = title.replace(/^Bestseller\s*/i, '').replace(/\bAdd to Compare\b/ig, '').replace(/\s+/g, ' ').trim();
                    }
                    const priceText = priceEl ? ((priceEl.textContent || '').trim()) : (fallbackPrice ? fallbackPrice[0] : '');
                    const ratingText = ratingEl ? ((ratingEl.textContent || '').trim()) : '';
                    const image = imageEl ? (imageEl.getAttribute('src') || imageEl.getAttribute('data-src') || '') : '';

                    if (href && title && priceText) {
                        out.push({href, title, priceText, ratingText, image});
                    }
                }
                return out;
                """
            )

            products: List[Dict[str, Any]] = []
            for row in rows or []:
                if len(products) >= max_results:
                    break

                href = (row.get("href") or "").strip()
                title = (row.get("title") or "").strip()
                price = clean_price((row.get("priceText") or "").strip())

                if not href or not title or not price:
                    continue

                url = f"{FLIPKART_BASE_URL}{href}" if href.startswith("/") else href

                rating = None
                rating_text = (row.get("ratingText") or "").strip()
                if rating_text:
                    try:
                        rating = float(rating_text.split()[0])
                    except Exception:
                        rating = None

                products.append(
                    {
                        "title": title,
                        "price": price,
                        "url": url,
                        "image_url": row.get("image") or None,
                        "rating": rating,
                        "platform": "Flipkart",
                        "source": "flipkart.com",
                    }
                )

            return products
        except Exception as e:
            logger.warning(f"Flipkart Selenium DOM extraction failed: {e}")
            return []

    def _extract_product_data(self, item: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Extract product data from Flipkart search result item.

        Args:
            item: BeautifulSoup element representing a product

        Returns:
            Product dict or None if extraction failed
        """
        try:
            # Title
            title_elem = (
                item.find("a", {"class": "IRpwTa"})
                or item.find("div", {"class": "_4rR01T"})
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
            price_elem = item.find("div", {"class": "_30jeq3"}) or item.select_one("div[class*='Nx9bqj']")
            price = clean_price(price_elem.get_text(strip=True)) if price_elem else None
            if not price:
                text_blob = item.get_text(" ", strip=True)
                price_match = re.search(r"₹\s*([\d,]{4,})", text_blob)
                if price_match:
                    price = clean_price(f"₹{price_match.group(1)}")

            # Product URL
            link_elem = (
                item.find("a", {"class": "IRpwTa"})
                or item.find("a", {"class": "_1fQZEK"})
                or item.select_one("a[href*='/p/']")
            )
            url = None
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                url = f"{FLIPKART_BASE_URL}{href}" if href.startswith("/") else href

            # Image URL
            image_elem = item.find("img")
            image_url = None
            if image_elem:
                image_url = image_elem.get("src") or image_elem.get("data-src")

            # Rating
            rating_elem = item.find("div", {"class": "_3LWZlK"})
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
                "platform": "Flipkart",
                "source": "flipkart.com",
            }

        except Exception as e:
            logger.debug(f"Error extracting product data: {e}")
            return None
        

        
