"""
Debug script for testing Selenium scrapers independently.
Run this to diagnose scraping issues without the full API.

Usage:
    python debug_scrapers.py
"""

import logging
import sys
from typing import Dict, Any

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scraper_debug.log"),
    ],
)

logger = logging.getLogger(__name__)

# Import scrapers
from services.amazon_service import AmazonService
from services.flipkart_service import FlipkartService
from services.croma_service import CromaService


def test_amazon() -> None:
    """Test Amazon scraper."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Amazon Scraper")
    logger.info("=" * 80)
    
    try:
        service = AmazonService()
        query = "iphone 15"
        logger.info(f"Searching for: {query}")
        
        results = service.search_products(query, max_results=5)
        
        logger.info(f"\n✅ Amazon Results: {len(results)} products found")
        for i, product in enumerate(results, 1):
            logger.info(f"\nProduct {i}:")
            logger.info(f"  Name: {product.get('name', 'N/A')[:60]}...")
            logger.info(f"  Price: ${product.get('price', 'N/A')}")
            logger.info(f"  Rating: {product.get('rating', 'N/A')}")
            logger.info(f"  URL: {product.get('product_url', 'N/A')}")
    
    except Exception as e:
        logger.error(f"❌ Amazon scraper error: {str(e)}", exc_info=True)


def test_flipkart() -> None:
    """Test Flipkart scraper."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Flipkart Scraper")
    logger.info("=" * 80)
    
    try:
        service = FlipkartService()
        query = "iphone 15"
        logger.info(f"Searching for: {query}")
        
        results = service.search_products(query, max_results=5)
        
        logger.info(f"\n✅ Flipkart Results: {len(results)} products found")
        for i, product in enumerate(results, 1):
            logger.info(f"\nProduct {i}:")
            logger.info(f"  Name: {product.get('name', 'N/A')[:60]}...")
            logger.info(f"  Price: ${product.get('price', 'N/A')}")
            logger.info(f"  Rating: {product.get('rating', 'N/A')}")
            logger.info(f"  URL: {product.get('product_url', 'N/A')}")
    
    except Exception as e:
        logger.error(f"❌ Flipkart scraper error: {str(e)}", exc_info=True)


def test_croma() -> None:
    """Test Croma scraper."""
    logger.info("\n" + "=" * 80)
    logger.info("Testing Croma Scraper")
    logger.info("=" * 80)
    
    try:
        service = CromaService()
        query = "iphone 15"
        logger.info(f"Searching for: {query}")
        
        results = service.search_products(query, max_results=5)
        
        logger.info(f"\n✅ Croma Results: {len(results)} products found")
        for i, product in enumerate(results, 1):
            logger.info(f"\nProduct {i}:")
            logger.info(f"  Name: {product.get('name', 'N/A')[:60]}...")
            logger.info(f"  Price: ${product.get('price', 'N/A')}")
            logger.info(f"  Rating: {product.get('rating', 'N/A')}")
            logger.info(f"  URL: {product.get('product_url', 'N/A')}")
    
    except Exception as e:
        logger.error(f"❌ Croma scraper error: {str(e)}", exc_info=True)


def main() -> None:
    """Run all scraper tests."""
    logger.info("Starting Scraper Debug Session...")
    logger.info(f"Query: iphone 15")
    
    test_amazon()
    test_flipkart()
    test_croma()
    
    logger.info("\n" + "=" * 80)
    logger.info("Debug session complete. Check scraper_debug.log for details.")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
