"""
Amazon India direct scraper using BeautifulSoup.
Fetches product data from amazon.in search results.
"""

import logging
from typing import List, Dict, Any, Optional
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from utils.scraper_utils import get_session_with_retries, get_headers, clean_price

logger = logging.getLogger(__name__)

AMAZON_BASE_URL = "https://www.amazon.in"
AMAZON_SEARCH_URL = f"{AMAZON_BASE_URL}/s"

# Headers to avoid being blocked
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}


class AmazonService:
    """
    Scrapes products from Amazon India.
    Handles pagination and product attribute extraction.
    """

    def __init__(self) -> None:
        self.session = get_session_with_retries(retries=3, backoff_factor=0.5)

    def _request_headers(self) -> Dict[str, str]:
        headers = get_headers()
        headers.update(
            {
                "Host": "www.amazon.in",
                "Referer": "https://www.amazon.in/",
                "DNT": "1",
            }
        )
        return headers

    def _normalize_text(self, text: str) -> str:
        """Lowercase and normalize text for token matching."""
        normalized = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
        return " ".join(normalized.split())

    def _required_query_terms(self, query: str) -> List[str]:
        """Extract meaningful query terms that should appear in title."""
        stopwords = {
            "mobile",
            "smartphone",
            "phone",
            "gb",
            "ram",
            "5g",
            "with",
            "and",
        }

        terms = []
        for token in self._normalize_text(query).split():
            if token in stopwords:
                continue
            if len(token) <= 1:
                continue
            terms.append(token)

        # Keep order and remove duplicates
        unique_terms: List[str] = []
        seen = set()
        for term in terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        return unique_terms

    def _title_matches_query(self, title: str, required_terms: List[str]) -> bool:
        """Check whether title contains all required query terms."""
        if not required_terms:
            return True

        normalized_title = self._normalize_text(title)
        return all(term in normalized_title for term in required_terms)

    def search_products(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search Amazon India for products.

        Args:
            query: Product search query
            max_results: Maximum number of results

        Returns:
            List of product dicts with: title, price, url, image_url, platform
        """
        try:
            products = []
            required_terms = self._required_query_terms(query)
            # Keep API responsive on mobile by limiting crawl depth.
            max_pages = 1

            for page in range(1, max_pages + 1):
                try:
                    # Build search URL
                    search_url = f"{AMAZON_SEARCH_URL}?{urlencode({'k': query, 'page': page})}"
                    logger.debug(f"Fetching Amazon page {page}: {search_url}")

                    # Fetch page
                    response = self.session.get(
                        search_url,
                        headers=self._request_headers(),
                        timeout=6,
                    )
                    response.raise_for_status()

                    # Parse HTML
                    soup = BeautifulSoup(response.content, "html.parser")
                    items = soup.find_all("div", {"data-component-type": "s-search-result"})

                    logger.debug(f"Found {len(items)} items on page {page}")

                    for item in items:
                        try:
                            product = self._extract_product_data(item)
                            if product and self._title_matches_query(
                                product.get("title", ""),
                                required_terms,
                            ):
                                products.append(product)

                            if len(products) >= max_results:
                                break
                        except Exception as e:
                            logger.debug(f"Error extracting product from Amazon: {e}")
                            continue

                    if len(products) >= max_results:
                        break

                except Exception as e:
                    logger.warning(f"Error scraping Amazon page {page}: {e}")
                    continue

            logger.info(f"Successfully scraped {len(products)} products from Amazon")
            return products[:max_results]

        except Exception as e:
            logger.error(f"Amazon scraping error: {e}")
            return []

    def _extract_product_data(self, item: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Extract product data from Amazon search result item.

        Args:
            item: BeautifulSoup element representing a product

        Returns:
            Product dict or None if extraction failed
        """
        try:
            # Title (prefer full title span under h2 > a)
            title_elem = (
                item.select_one("h2 a span")
                or item.select_one("h2 span.a-size-medium")
                or item.select_one("span.a-size-medium.a-color-base.a-text-normal")
                or item.find("h2")
            )

            title = " ".join(title_elem.stripped_strings) if title_elem else ""

            # Fallback to image alt if selector returns only short brand text
            if len(title.split()) < 3:
                image_elem_fallback = item.find("img", {"class": "s-image"})
                if image_elem_fallback:
                    alt_title = (image_elem_fallback.get("alt") or "").strip()
                    if len(alt_title.split()) >= 3:
                        title = alt_title

            # Reject obviously incomplete titles (e.g., "Samsung")
            if not title or len(title.split()) < 3:
                return None

            # Price (in INR)
            price_whole = item.select_one("span.a-price > span.a-offscreen")
            if not price_whole:
                price_whole = item.find("span", {"class": "a-price-whole"})
            price = clean_price(price_whole.get_text(strip=True)) if price_whole else None

            # Product URL
            link_elem = item.select_one("h2 a") or item.select_one("a.a-link-normal")
            url = None
            if link_elem and link_elem.get("href"):
                href = link_elem["href"]
                url = f"{AMAZON_BASE_URL}{href}" if href.startswith("/") else href

            # Image URL
            image_elem = item.find("img", {"class": "s-image"})
            image_url = image_elem.get("src") if image_elem else None

            # Rating
            rating_elem = item.select_one("span.a-icon-alt")
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
                "platform": "Amazon",
                "source": "amazon.in",
            }

        except Exception as e:
            logger.debug(f"Error extracting product data: {e}")
            return None

