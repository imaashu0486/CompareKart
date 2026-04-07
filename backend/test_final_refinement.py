"""Test FINAL REFINEMENT strict filtering."""
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, 'backend')
from main import app

c = TestClient(app)

print('=== FINAL REFINEMENT TEST ===\n')

# Test 1: Valid iPhone query
print('Test 1: Valid iPhone 14 Pro 128GB')
r = c.get('/api/products/search?query=iPhone 14 Pro 128GB&limit=10')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Total groups: {data["total_groups"]}')
print(f'Total offers: {data["total_offers"]}')
if data['product_groups']:
    for g in data['product_groups'][:2]:
        print(f'  - {g["product_name"]}: {g["offer_count"]} offers (Best: Rs {g["best_price"]})')
print()

# Test 2: Query with RAM specification
print('Test 2: With RAM specification (iPhone 15 12GB RAM 256GB)')
r = c.get('/api/products/search?query=iPhone 15 12GB RAM 256GB&limit=10')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Total groups: {data["total_groups"]}')
print(f'Total offers: {data["total_offers"]}')
print()

# Test 3: Samsung S24 Ultra
print('Test 3: Samsung Galaxy S24 Ultra 256GB')
r = c.get('/api/products/search?query=Samsung Galaxy S24 Ultra 256GB&limit=10')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Total groups: {data["total_groups"]}')
print(f'Total offers: {data["total_offers"]}')
print()

# Test 4: No storage (should fail)
print('Test 4: Invalid - no storage specified')
r = c.get('/api/products/search?query=iPhone 14 Pro&limit=10')
print(f'Status: {r.status_code}')
if r.status_code != 200:
    print(f'Error: {r.json()["detail"]}')
print()

# Test 5: Too short (should fail)
print('Test 5: Invalid - too short')
r = c.get('/api/products/search?query=iPhone&limit=10')
print(f'Status: {r.status_code}')
if r.status_code != 200:
    print(f'Error: {r.json()["detail"]}')
print()

# Test 6: Valid OnePlus
print('Test 6: OnePlus 12 Pro 256GB')
r = c.get('/api/products/search?query=OnePlus 12 Pro 256GB&limit=10')
print(f'Status: {r.status_code}')
data = r.json()
print(f'Total groups: {data["total_groups"]}')
print(f'Total offers: {data["total_offers"]}')

print('\n=== ALL TESTS COMPLETE ===')
