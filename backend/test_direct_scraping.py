"""
Quick test for direct platform scraping implementation.
Tests the complete flow from query to grouped comparison.
"""

import logging
from services.aggregator import ProductAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def test_direct_scraping():
    """Test direct platform scraping with a sample query."""
    
    print("\n" + "="*60)
    print("TESTING DIRECT PLATFORM SCRAPING")
    print("="*60 + "\n")
    
    # Initialize aggregator
    aggregator = ProductAggregator()
    
    # Test query
    query = "iPhone 14 Pro 128GB"
    print(f"Query: {query}\n")
    
    # Perform search
    print("Scraping platforms...")
    result = aggregator.search_and_compare(query)
    
    # Display results
    print("\n" + "-"*60)
    print("RESULTS")
    print("-"*60)
    print(f"Query: {result.query}")
    print(f"Found: {result.found}")
    print(f"Message: {result.message}")
    print(f"Product Groups: {len(result.product_groups)}")
    
    if result.product_groups:
        print("\n" + "-"*60)
        print("GROUP DETAILS")
        print("-"*60)
        
        for idx, group in enumerate(result.product_groups, 1):
            variant = group.get("variant", {})
            offers = group.get("offers", [])
            
            print(f"\nGroup {idx}:")
            print(f"  Variant: {variant.get('brand')} {variant.get('model')} {variant.get('storage')}")
            print(f"  Best Price: ₹{group.get('best_price'):,.2f}")
            print(f"  Offer Count: {group.get('offer_count')}")
            print(f"  Offers:")
            
            for offer in offers:
                print(f"    - {offer.get('platform')}: ₹{offer.get('price'):,.2f}")
                print(f"      URL: {offer.get('url')[:60]}...")
    else:
        print("\nNo product groups found.")
        print("This is expected if scraping fails or no products match filters.")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_direct_scraping()
