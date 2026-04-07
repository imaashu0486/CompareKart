"""Debug why products are being filtered."""
from services.aggregator import ProductAggregator
from utils.scraper_utils import (
    is_valid_platform,
    is_new_condition,
    extract_mobile_attributes,
    is_valid_price,
)

agg = ProductAggregator()

print('=== DEBUG FILTERING ===\n')

# Get raw products from SerpAPI
products = agg.search_products("iPhone 14 Pro 128GB", 30)
print(f'Found {len(products)} products\n')

if products:
    for i, p in enumerate(products[:5]):
        print(f'Product {i+1}:')
        print(f'  Title: {p.get("title")}')
        print(f'  Platform: {p.get("platform")}')
        print(f'  Price: {p.get("price")}')
        
        # Test each filter
        valid_platform = is_valid_platform(p.get("platform"))
        print(f'  - Valid platform: {valid_platform}')
        
        if valid_platform:
            new_cond = is_new_condition(p.get("title"))
            print(f'  - New condition: {new_cond}')
            
            if new_cond:
                attrs = extract_mobile_attributes(p.get("title"))
                print(f'  - Extract attrs: {attrs}')
                
                if attrs:
                    valid_price = is_valid_price(p.get("price"))
                    print(f'  - Valid price: {valid_price}')
        print()
