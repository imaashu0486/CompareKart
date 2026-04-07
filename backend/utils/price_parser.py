"""
Safe price parsing utility.
Handles various price formats and currency symbols.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)


def parse_price(price_string: Optional[str]) -> Optional[float]:
    """
    Parse price from various formats.

    Handles:
    - Currency symbols: $, ₹, €, £, ¥
    - Thousand separators: commas and spaces
    - Decimal points
    - Whitespace

    Args:
        price_string: Raw price string (e.g., "$1,299.00", "₹9,999")

    Returns:
        Float price or None if parsing fails

    Examples:
        >>> parse_price("$99.99")
        99.99
        >>> parse_price("₹9,999.00")
        9999.0
        >>> parse_price("€1,299")
        1299.0
    """
    if not price_string:
        return None

    try:
        # Convert to string and strip whitespace
        price_text = str(price_string).strip()

        if not price_text:
            return None

        # Remove currency symbols
        price_text = price_text.replace("₹", "")
        price_text = price_text.replace("$", "")
        price_text = price_text.replace("€", "")
        price_text = price_text.replace("£", "")
        price_text = price_text.replace("¥", "")
        price_text = price_text.replace("₦", "")

        # Remove common text patterns
        price_text = re.sub(r"[^\d.,]", "", price_text)

        if not price_text:
            return None

        # Handle various decimal/thousand separator patterns
        # European format: 1.234,56 -> 1234.56
        # US format: 1,234.56 -> 1234.56
        # Indian format: 1,23,456 or 1,23,456.78 -> 123456 or 123456.78

        if "," in price_text and "." in price_text:
            comma_pos = price_text.rfind(",")
            dot_pos = price_text.rfind(".")

            if comma_pos > dot_pos:
                # European format: comma is decimal separator
                price_text = price_text.replace(".", "").replace(",", ".")
            else:
                # US format: dot is decimal separator
                price_text = price_text.replace(",", "")
        elif "," in price_text:
            # Only commas - determine if thousand separator or decimal
            last_comma_pos = price_text.rfind(",")
            after_comma = price_text[last_comma_pos + 1 :]

            if len(after_comma) == 2:
                # Likely decimal separator (European)
                price_text = price_text.replace(".", "").replace(",", ".")
            elif len(after_comma) == 3:
                # Likely thousand separator (US/Indian)
                price_text = price_text.replace(",", "")
            else:
                # Default: remove all commas
                price_text = price_text.replace(",", "")

        # Convert to float
        price = float(price_text)

        # Validate: price should be reasonable
        if price < 0 or price > 999999999:
            logger.warning(f"Price out of reasonable range: {price}")
            return None

        return price

    except (ValueError, AttributeError) as e:
        logger.debug(f"Failed to parse price '{price_string}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error parsing price '{price_string}': {str(e)}")
        return None


def safe_sort_by_price(products: list, reverse: bool = False) -> list:
    """
    Sort products by price safely, filtering out None prices.

    Args:
        products: List of product dictionaries
        reverse: Sort descending if True, ascending if False

    Returns:
        Sorted list of products (price >= 0 only)
    """
    if not products:
        return []

    try:
        # Filter out products without valid prices
        valid_products = [
            p for p in products
            if p.get("price") is not None and p.get("price") > 0
        ]

        # Sort by price
        sorted_products = sorted(
            valid_products,
            key=lambda x: float(x.get("price", float("inf"))),
            reverse=reverse,
        )

        return sorted_products

    except Exception as e:
        logger.error(f"Error sorting products by price: {str(e)}")
        return [p for p in products if p.get("price")]
