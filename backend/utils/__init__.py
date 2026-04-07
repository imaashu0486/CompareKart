"""
Initialization file for utils.
"""

from utils.scraper_utils import (
    get_headers,
    get_session_with_retries,
    fetch_page,
    clean_price,
    normalize_product_name,
    calculate_similarity,
)
from utils.price_parser import parse_price, safe_sort_by_price

__all__ = [
    "get_headers",
    "get_session_with_retries",
    "fetch_page",
    "clean_price",
    "normalize_product_name",
    "calculate_similarity",
    "parse_price",
    "safe_sort_by_price",
]

