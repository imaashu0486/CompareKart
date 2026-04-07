"""Debug FINAL REFINEMENT filtering."""
from fastapi.testclient import TestClient
import sys
import json
sys.path.insert(0, 'backend')
from main import app
from services.aggregator import ProductAggregator

agg = ProductAggregator()

print('=== DEBUG FINAL REFINEMENT ===\n')

# Get raw products from SerpAPI
print('Raw products from SerpAPI for "iPhone 14 Pro 128GB":')
products = agg.search_products("iPhone 14 Pro 128GB", 10)
print(f'Found {len(products)} products\n')

if products:
    for i, p in enumerate(products[:3]):
        print(f'Product {i+1}:')
        print(f'  Title: {p.get("title")}')
        print(f'  Platform: {p.get("platform")}')
        print(f'  Price: {p.get("price")}')
        print(f'  URL: {p.get("url")[:80]}...')
        print()

# Test storage matching
print('\n=== Test Storage Matching ===')
from utils.scraper_utils import (
    extract_storage_from_query,
    storage_matches_exactly,
    extract_mobile_attributes,
    is_valid_platform,
    is_new_condition,
    is_valid_price,
)

query = "iPhone 14 Pro 128GB"
query_storage = extract_storage_from_query(query)
print(f'Query storage: {query_storage}')

if products:
    p = products[0]
    print(f'Product title: {p.get("title")}')
    print(f'Storage match: {storage_matches_exactly(p.get("title"), query_storage)}')
    print(f'Valid platform: {is_valid_platform(p.get("platform"))}')
    print(f'New condition: {is_new_condition(p.get("title"))}')
    print(f'Valid price: {is_valid_price(p.get("price"))}')
    print(f'Extract attrs: {extract_mobile_attributes(p.get("title"))}')
