"""
Platform scraper coordinator for Indian e-commerce sites.
Orchestrates scraping from multiple platforms and aggregates results.
"""

import logging
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from services.amazon_service import AmazonService
from services.flipkart_service import FlipkartService
from services.croma_service import CromaService

logger = logging.getLogger(__name__)


class PlatformScraper:
    """
    Coordinates scraping from all Indian e-commerce platforms.
    Collects and aggregates product data.
    """

    def __init__(self):
        """Initialize scrapers for all platforms."""
        self.amazon = AmazonService()
        self.flipkart = FlipkartService()
        self.croma = CromaService()

    def search_all_platforms(
        self,
        query: str,
        max_results_per_platform: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Search for products across all Indian e-commerce platforms.

        Args:
            query: Product search query
            max_results_per_platform: Max results per platform

        Returns:
            Combined list of products from all platforms
        """
        all_products = []

        # Search each platform concurrently to minimize API latency.
        logger.info(f"Searching all platforms for: {query}")
        platform_calls = {
            "Amazon": self.amazon.search_products,
            "Flipkart": self.flipkart.search_products,
            "Croma": self.croma.search_products,
        }

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = {
                executor.submit(search_fn, query, max_results_per_platform): platform_name
                for platform_name, search_fn in platform_calls.items()
            }

            for future in as_completed(futures):
                platform_name = futures[future]
                try:
                    platform_products = future.result()
                    logger.info(f"Found {len(platform_products)} products on {platform_name}")
                    all_products.extend(platform_products)
                except Exception as e:
                    logger.error(f"{platform_name} search failed: {str(e)}")

        logger.info(f"Total products collected: {len(all_products)}")
        return all_products
