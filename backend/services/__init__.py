"""
Initialization file for services.
"""

from services.aggregator import ProductAggregator
from services.platform_scraper import PlatformScraper
from services.amazon_service import AmazonService
from services.flipkart_service import FlipkartService
from services.croma_service import CromaService

__all__ = [
    "ProductAggregator",
    "PlatformScraper",
    "AmazonService",
    "FlipkartService",
    "CromaService",
]


