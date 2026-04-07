"""
Aggregator for direct platform scraping comparison results.
Implements strict variant-level matching with no fuzzy logic.
"""

import logging
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
from sqlalchemy import func
from services.platform_scraper import PlatformScraper
from utils.scraper_utils import (
    extract_mobile_attributes,
    is_valid_price,
)

logger = logging.getLogger(__name__)

# Price range constraints for Indian market
MIN_PRICE_INR = 20000
MAX_PRICE_INR = 200000


@dataclass
class ProductGroup:
    """Grouped comparison results."""
    group_id: str
    brand: str
    model: str
    storage: str
    products: List[Dict[str, Any]]
    min_price: float
    best_price_url: str


@dataclass
class GroupedComparisonResult:
    """Final response structure."""
    query: str
    found: bool
    message: str
    product_groups: List[Dict[str, Any]]


class ProductAggregator:
    """
    Aggregates results from direct platform scrapers.
    Performs strict variant-level matching.
    """

    def __init__(self):
        """Initialize scraper and utilities."""
        self.scraper = PlatformScraper()

    def _extract_query_constraints(self, query: str) -> Dict[str, Optional[str]]:
        """
        Extract brand/model/storage constraints from query.

        Supports both strict queries with storage and lighter model-only queries.
        """
        q = (query or "").lower().strip()
        if not q:
            return {
                "brand": None,
                "model": None,
                "storage": None,
                "family_match": False,
            }

        storage_match = re.search(r"(\d+)\s?gb", q)
        storage = f"{storage_match.group(1)}gb" if storage_match else None

        brand = None
        model = None
        family_match = False

        # Apple
        if "iphone" in q:
            brand = "apple"
            m = re.search(r"iphone\s*(\d+)\s*(pro\s*max|pro|plus|mini|e)?", q)
            if m:
                number = m.group(1)
                variant = (m.group(2) or "").strip()
                model = f"iphone {number} {variant}".strip()
                # If variant is absent, allow family-level match (e.g., "iphone 17")
                family_match = variant == ""

        # Samsung
        elif "galaxy" in q or re.search(r"\bs\d{2}\b", q):
            brand = "samsung"
            m = re.search(r"(?:galaxy\s*)?s(\d+)\s*(ultra|\+|plus)?", q)
            if m:
                number = m.group(1)
                variant = (m.group(2) or "").strip()
                model = f"galaxy s{number} {variant}".strip()
                family_match = variant == ""

        # OnePlus
        elif "oneplus" in q or "one plus" in q:
            brand = "oneplus"
            m = re.search(r"(?:oneplus|one\s*plus)\s*(\d+)\s*(t|pro)?", q)
            if m:
                number = m.group(1)
                variant = (m.group(2) or "").strip()
                model = f"oneplus {number} {variant}".strip()
                family_match = variant == ""

        # Oppo
        elif "oppo" in q:
            brand = "oppo"
            m = re.search(
                r"oppo\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|lite|neo)?",
                q,
            )
            if m:
                series = (m.group(1) or "").strip()
                variant = (m.group(2) or "").replace("  ", " ").strip()
                model = f"oppo {series} {variant}".strip()
                family_match = variant == ""

        # Realme
        elif "realme" in q:
            brand = "realme"
            m = re.search(
                r"realme\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra)?",
                q,
            )
            if m:
                series = (m.group(1) or "").strip()
                variant = (m.group(2) or "").replace("  ", " ").strip()
                model = f"realme {series} {variant}".strip()
                family_match = variant == ""

        # Vivo
        elif "vivo" in q:
            brand = "vivo"
            m = re.search(
                r"vivo\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra)?",
                q,
            )
            if m:
                series = (m.group(1) or "").strip()
                variant = (m.group(2) or "").replace("  ", " ").strip()
                model = f"vivo {series} {variant}".strip()
                family_match = variant == ""

        # Xiaomi / Redmi / Poco
        elif "xiaomi" in q or "redmi" in q:
            brand = "xiaomi"
            m = re.search(
                r"(?:xiaomi|redmi)\s*(?:note\s*)?([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra)?",
                q,
            )
            if m:
                series = (m.group(1) or "").strip()
                variant = (m.group(2) or "").replace("  ", " ").strip()
                note_prefix = "note " if "note" in q else ""
                model = f"xiaomi {note_prefix}{series} {variant}".strip()
                family_match = variant == ""
        elif "poco" in q:
            brand = "poco"
            m = re.search(
                r"poco\s*([a-z]*\d+[a-z0-9]*)\s*(pro\s*plus|pro\+|pro|max|plus|ultra|gt)?",
                q,
            )
            if m:
                series = (m.group(1) or "").strip()
                variant = (m.group(2) or "").replace("  ", " ").strip()
                model = f"poco {series} {variant}".strip()
                family_match = variant == ""

        return {
            "brand": brand,
            "model": model,
            "storage": storage,
            "family_match": family_match,
        }

    def _matches_query(self, product: Dict[str, Any], query_constraints: Dict[str, Optional[str]]) -> bool:
        """Return True if enriched product matches parsed query constraints."""
        if not query_constraints:
            return True

        query_brand = query_constraints.get("brand")
        query_model = query_constraints.get("model")
        query_storage = query_constraints.get("storage")
        family_match = bool(query_constraints.get("family_match"))

        product_brand = (product.get("brand") or "").lower().strip()
        product_model = (product.get("model") or "").lower().strip()
        product_storage = (product.get("storage") or "").lower().strip()

        if query_brand and product_brand != query_brand:
            return False

        if query_model:
            if family_match:
                if not product_model.startswith(query_model):
                    return False
            elif product_model != query_model:
                return False

        if query_storage and product_storage != query_storage:
            return False

        return True

    def search_and_compare(self, query: str) -> GroupedComparisonResult:
        """
        Search all platforms and return grouped comparison.

        Args:
            query: Mobile device search query

        Returns:
            GroupedComparisonResult with grouped products
        """
        try:
            logger.info(f"Starting comparison search for: {query}")

            # Scrape all platforms
            all_products = self.scraper.search_all_platforms(query, max_results_per_platform=10)
            logger.info(f"Total products scraped: {len(all_products)}")
            query_constraints = self._extract_query_constraints(query)

            if not all_products:
                return GroupedComparisonResult(
                    query=query,
                    found=False,
                    message="No products found across Indian e-commerce platforms",
                    product_groups=[],
                )

            # Extract attributes and filter
            enriched_products = []
            for product in all_products:
                enriched = self._enrich_product(product)
                if enriched and self._matches_query(enriched, query_constraints):
                    enriched_products.append(enriched)

            logger.info(f"Products after filtering: {len(enriched_products)}")

            if not enriched_products:
                return GroupedComparisonResult(
                    query=query,
                    found=False,
                    message="No valid mobile products found after filtering",
                    product_groups=[],
                )

            # Group by exact variant match
            groups = self._group_by_exact_match(enriched_products)
            logger.info(f"Product groups created: {len(groups)}")

            # Keep groups with at least one offer for broader result coverage.
            valid_groups = [g for g in groups if len(g.products) >= 1]
            logger.info(f"Valid groups (1+ offers): {len(valid_groups)}")

            if not valid_groups:
                return GroupedComparisonResult(
                    query=query,
                    found=False,
                    message="No valid product variants available",
                    product_groups=[],
                )

            # Convert to response format
            product_groups = [self._group_to_dict(g) for g in valid_groups]

            return GroupedComparisonResult(
                query=query,
                found=True,
                message=f"Found {len(valid_groups)} product variants",
                product_groups=product_groups,
            )

        except Exception as e:
            logger.error(f"Comparison error: {e}", exc_info=True)
            return GroupedComparisonResult(
                query=query,
                found=False,
                message="Error processing comparison request",
                product_groups=[],
            )

    def _enrich_product(self, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enrich product with extracted mobile attributes.

        Args:
            product: Raw product from scraper

        Returns:
            Enriched product or None if filtering fails
        """
        try:
            title = product.get("title", "")
            price = product.get("price")
            url = product.get("url")

            # Validate price
            if not price or not is_valid_price(price):
                logger.debug(f"Invalid price: {price}")
                return None

            if price < MIN_PRICE_INR or price > MAX_PRICE_INR:
                logger.debug(f"Price out of range: {price} INR")
                return None

            # Extract mobile attributes (STRICT - requires brand, model, storage)
            attributes = extract_mobile_attributes(title)
            if not attributes:
                logger.debug(f"Could not extract mobile attributes from: {title}")
                return None

            brand = attributes.get("brand")
            model = attributes.get("model")
            storage = attributes.get("storage")
            condition = attributes.get("condition", "unknown")

            # STRICT: All of brand, model, storage are REQUIRED
            if not brand or not model or not storage:
                logger.debug(
                    f"Missing required attributes - Brand: {brand}, Model: {model}, Storage: {storage}"
                )
                return None

            # STRICT: Only "new" condition accepted
            if condition != "new":
                logger.debug(f"Not new condition: {condition}")
                return None

            return {
                "title": title,
                "price": float(price),
                "url": url,
                "image_url": product.get("image_url"),
                "platform": product.get("platform", "Unknown"),
                "rating": product.get("rating"),
                "source": product.get("source", ""),
                "brand": brand,
                "model": model,
                "storage": storage,
                "condition": condition,
            }

        except Exception as e:
            logger.debug(f"Error enriching product: {e}")
            return None

    def _group_by_exact_match(self, products: List[Dict[str, Any]]) -> List[ProductGroup]:
        """
        Group products by exact brand+model+storage match.

        Args:
            products: Enriched products with attributes

        Returns:
            List of ProductGroup objects
        """
        groups_dict: Dict[str, List[Dict[str, Any]]] = {}

        for product in products:
            brand = product.get("brand", "")
            model = product.get("model", "")
            storage = product.get("storage", "")

            # Exact group key - no fuzzy matching
            group_id = f"{brand}_{model}_{storage}".lower().replace(" ", "_")

            if group_id not in groups_dict:
                groups_dict[group_id] = []

            groups_dict[group_id].append(product)

        # Convert to ProductGroup objects
        groups = []
        for group_id, products_list in groups_dict.items():
            # Sort by price (ascending)
            products_list.sort(key=lambda x: x.get("price", float("inf")))

            best_price = products_list[0].get("price", 0)
            best_url = products_list[0].get("url", "")

            group = ProductGroup(
                group_id=group_id,
                brand=products_list[0]["brand"],
                model=products_list[0]["model"],
                storage=products_list[0]["storage"],
                products=products_list,
                min_price=best_price,
                best_price_url=best_url,
            )
            groups.append(group)

        # Sort by best price
        groups.sort(key=lambda g: g.min_price)

        return groups

    def _group_to_dict(self, group: ProductGroup) -> Dict[str, Any]:
        """
        Convert ProductGroup to response dictionary.

        Args:
            group: ProductGroup object

        Returns:
            Dictionary for JSON response
        """
        # Include only essential fields for each product
        products = [
            {
                "title": p["title"],
                "price": p["price"],
                "url": p["url"],
                "image_url": p.get("image_url"),
                "platform": p["platform"],
                "rating": p.get("rating"),
            }
            for p in group.products
        ]

        return {
            "variant": {
                "brand": group.brand,
                "model": group.model,
                "storage": group.storage,
            },
            "offers": products,
            "best_price": group.min_price,
            "offer_count": len(products),
        }

    def aggregate_comparison(
        self,
        query: str,
        max_results: int = 30,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """
        Aggregate product offers into flat comparison response used by /compare.

        Args:
            query: Search query
            max_results: Maximum flattened products to return
            db: Optional database session

        Returns:
            Dictionary compatible with ComparisonResult schema
        """
        try:
            per_platform = max(1, min(max_results, 30))
            query_constraints = self._extract_query_constraints(query)
            raw_products = self.scraper.search_all_platforms(
                query=query,
                max_results_per_platform=per_platform,
            )

            enriched_products: List[Dict[str, Any]] = []
            for product in raw_products:
                enriched = self._enrich_product(product)
                if enriched and self._matches_query(enriched, query_constraints):
                    enriched_products.append(enriched)

            # Deduplicate by URL, keep cheapest duplicate
            by_url: Dict[str, Dict[str, Any]] = {}
            for product in enriched_products:
                url = product.get("url") or ""
                if not url:
                    continue
                existing = by_url.get(url)
                if existing is None or product["price"] < existing["price"]:
                    by_url[url] = product

            products = sorted(by_url.values(), key=lambda x: x["price"])[:max_results]

            if db is not None and products:
                self._persist_search_results(db=db, query=query, products=products)

            prices = [p["price"] for p in products]
            lowest_price = min(prices) if prices else 0
            highest_price = max(prices) if prices else 0

            response_products = [
                {
                    "title": p["title"],
                    "platform": p["platform"],
                    "price": p["price"],
                    "image_url": p.get("image_url"),
                    "url": p["url"],
                    "rating": p.get("rating"),
                    "rating_count": None,
                    "description": None,
                }
                for p in products
            ]

            return {
                "query": query,
                "total_results": len(response_products),
                "platform_count": len({p["platform"] for p in products}) if products else 0,
                "lowest_price": lowest_price,
                "highest_price": highest_price,
                "price_range": (highest_price - lowest_price) if products else 0,
                "best_deal": response_products[0] if response_products else None,
                "products": response_products,
            }

        except Exception as e:
            logger.error(f"aggregate_comparison failed: {e}", exc_info=True)
            return {
                "query": query,
                "total_results": 0,
                "platform_count": 0,
                "lowest_price": 0,
                "highest_price": 0,
                "price_range": 0,
                "best_deal": None,
                "products": [],
            }

    def get_detailed_comparison(
        self,
        product_id: int,
        db: Session,
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed comparison of a stored product against same-name products.

        Args:
            product_id: Database product id
            db: Active DB session

        Returns:
            Dictionary compatible with DetailedComparison schema or None
        """
        try:
            from models import Product

            base_product = db.query(Product).filter(Product.id == product_id).first()
            if not base_product:
                return None

            products = (
                db.query(Product)
                .filter(func.lower(Product.name) == func.lower(base_product.name))
                .order_by(Product.price.asc())
                .all()
            )

            if not products:
                return None

            response_products = [
                {
                    "title": p.name,
                    "platform": p.platform,
                    "price": p.price,
                    "image_url": p.image_url,
                    "url": p.product_url,
                    "rating": p.rating,
                    "rating_count": p.rating_count,
                    "description": p.description,
                }
                for p in products
            ]

            prices = [p.price for p in products]
            return {
                "product_name": base_product.name,
                "results_count": len(products),
                "platforms_available": len({p.platform for p in products}),
                "price_stats": {
                    "min": min(prices),
                    "max": max(prices),
                    "avg": sum(prices) / len(prices),
                    "range": max(prices) - min(prices),
                },
                "products": response_products,
            }

        except Exception as e:
            logger.error(f"get_detailed_comparison failed: {e}", exc_info=True)
            return None

    def _persist_search_results(
        self,
        db: Session,
        query: str,
        products: List[Dict[str, Any]],
    ) -> None:
        """Persist search history and product snapshots in database."""
        try:
            from models import Product, SearchHistory

            for p in products:
                db.add(
                    Product(
                        name=p["title"],
                        platform=p["platform"],
                        price=float(p["price"]),
                        image_url=p.get("image_url"),
                        product_url=p["url"],
                        rating=p.get("rating"),
                        rating_count=None,
                        description=None,
                    )
                )

            db.add(
                SearchHistory(
                    query=query,
                    results_count=len(products),
                    platform_breakdown=", ".join(sorted({p["platform"] for p in products})),
                )
            )
            db.commit()
        except Exception as e:
            db.rollback()
            logger.warning(f"Failed to persist search results: {e}")
