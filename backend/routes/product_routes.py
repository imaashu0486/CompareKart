"""
Product search and comparison API routes.
Handles all product-related endpoints.
"""

import logging
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Product, SearchHistory
from schemas import ComparisonResult, DetailedComparison, ProductResponse
from services.aggregator import ProductAggregator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/products", tags=["products"])

# Initialize aggregator
aggregator = ProductAggregator()


@router.get("/search")
async def search_products(
    query: str = Query(..., min_length=1, max_length=255, description="Mobile model with storage (e.g., iPhone 14 Pro 128GB)"),
    limit: int = Query(30, ge=1, le=100, description="Maximum results to return"),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Search for mobile phones with strict filtering via direct scraping.
    
    Returns ONLY clean, legitimate Indian new-product offers from Amazon, Flipkart, Croma.

    **Strict Validation:**
    - Query must be 10+ characters
    - Query must contain storage (e.g., "128GB")
    - Direct scraping from amazon.in, flipkart.com, croma.com only
    - New condition only (rejects used, refurbished, resale)
    - Must have brand, model, storage extracted
    - Price must be realistic (₹20k-₹2L)
    - At least 2 offers per variant

    **Query Parameters:**
    - query: Mobile model with storage (required, min 10 chars)
    - limit: Maximum results (1-100, default: 30)

    **Examples:**
    - "iPhone 14 Pro 128GB"
    - "Samsung Galaxy S24 256GB"
    - "OnePlus 12 Pro 12GB RAM 256GB"

    **Response:**
    Returns groups only if 2+ offers from Indian platforms exist for exact variant.
    """
    try:
        import re
        query_stripped = query.strip()

        if len(query_stripped) < 10:
            raise HTTPException(
                status_code=400,
                detail="Query must be at least 10 characters. Example: iPhone 14 Pro 128GB",
            )
        
        # Validation: Must contain storage (regex: \d+\s?gb)
        if not re.search(r'\d+\s?gb', query_stripped.lower()):
            raise HTTPException(
                status_code=400,
                detail="Query must include storage capacity (e.g., 128GB, 256 GB). Example: iPhone 14 Pro 128GB",
            )
        
        # Validation: Must contain at least one number
        if not re.search(r'\d', query_stripped):
            raise HTTPException(
                status_code=400,
                detail="Query must include storage capacity (e.g., 128GB). Example: iPhone 14 Pro 128GB",
            )

        logger.info(f"Search request: query={query}, limit={limit}")

        # Perform strict mobile comparison search with direct scraping
        result = aggregator.search_and_compare(query=query.strip())

        total_groups = len(result.product_groups)
        total_offers = sum(group.get("offer_count", 0) for group in result.product_groups)

        return {
            "query": result.query,
            "found": result.found,
            "message": result.message,
            "total_groups": total_groups,
            "total_offers": total_offers,
            "product_groups": result.product_groups,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during search",
        )


@router.get("/compare")
async def compare_products(
    query: str = Query(..., min_length=1, max_length=255, description="Product search query"),
    limit: int = Query(20, ge=1, le=50, description="Maximum results per platform"),
    db: Session = Depends(get_db),
) -> ComparisonResult:
    """
    Compare products across platforms with detailed metrics.

    Returns products sorted by price with statistics.

    **Query Parameters:**
    - query: Search term (required)
    - limit: Results per platform (1-50, default: 20)

    **Response:**
    Detailed comparison with price range, best deal identification.
    """
    try:
        result = aggregator.aggregate_comparison(
            query=query.strip(),
            max_results=limit * 3,
            db=db,
        )

        if result.get("total_results", 0) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for query: {query}",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Comparison error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during comparison",
        )


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
) -> ProductResponse:
    """
    Get detailed information about a specific product.

    **Parameters:**
    - product_id: Product ID from database

    **Response:**
    Complete product details including pricing and availability.
    """
    try:
        product: Optional[Product] = db.query(Product).filter(
            Product.id == product_id
        ).first()

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found",
            )

        return ProductResponse.from_orm(product)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.get("/{product_id}/comparison")
async def get_product_comparison(
    product_id: int,
    db: Session = Depends(get_db),
) -> DetailedComparison:
    """
    Get detailed comparison of a product across all platforms.

    Shows the same product available on different platforms with price differences.

    **Parameters:**
    - product_id: Product ID from database

    **Response:**
    Detailed comparison including price statistics and platform availability.
    """
    try:
        result: Optional[DetailedComparison] = aggregator.get_detailed_comparison(
            product_id,
            db,
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Product with ID {product_id} not found",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting comparison for product {product_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.get("/platform/{platform}/trending")
async def get_trending_by_platform(
    platform: str,
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db),
) -> list[ProductResponse]:
    """
    Get trending products from a specific platform.

    Based on search history and recent queries.

    **Parameters:**
    - platform: E-commerce platform name
    - limit: Number of results

    **Response:**
    List of trending products from the specified platform.
    """
    try:
        valid_platforms = ["Amazon", "Flipkart", "Croma", "eBay"]
        if platform not in valid_platforms:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid platform. Must be one of: {', '.join(valid_platforms)}",
            )

        products = db.query(Product).filter(
            Product.platform == platform,
        ).order_by(
            Product.last_updated.desc(),
        ).limit(limit).all()

        return [ProductResponse.from_orm(p) for p in products]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trending products: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )


@router.get("/stats/search-history")
async def get_search_history(
    limit: int = Query(20, ge=1, le=100, description="Number of recent searches"),
    db: Session = Depends(get_db),
) -> list[dict]:
    """
    Get recent search history for analytics.

    **Parameters:**
    - limit: Number of recent searches to return

    **Response:**
    List of recent searches with timestamps and result counts.
    """
    try:
        searches = db.query(SearchHistory).order_by(
            SearchHistory.timestamp.desc(),
        ).limit(limit).all()

        return [
            {
                "id": s.id,
                "query": s.query,
                "timestamp": s.timestamp,
                "results_count": s.results_count,
            }
            for s in searches
        ]

    except Exception as e:
        logger.error(f"Error getting search history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error",
        )
