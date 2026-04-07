"""Test strict mobile engine Phase 1."""
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, 'backend')
from main import app

c = TestClient(app)

# Test validation
print("=== VALIDATION TESTS ===")
r = c.get('/api/products/search?query=iPhone')
print(f"Too short query: {r.status_code} - {'PASS' if r.status_code == 400 else 'FAIL'}")

r = c.get('/api/products/search?query=abc def ghi jkl')
print(f"No storage query: {r.status_code} - {'PASS' if r.status_code == 400 else 'FAIL'}")

# Test strict matching
print("\n=== STRICT MATCHING TEST ===")
r = c.get('/api/products/search?query=iPhone14Pro128GB')
print(f"Valid query status: {r.status_code}")
data = r.json()
print(f"Groups (exact variant match): {data['total_groups']}")
print(f"Offers (2+ per group): {data['total_offers']}")

if data['product_groups']:
    print("\nTop groups:")
    for g in data['product_groups'][:3]:
        print(f"  {g['product_name']}")
        print(f"    Offers: {g['offer_count']}, Best: ${g['best_price']:.0f}")
else:
    print("No groups found (requires 2+ offers of same variant)")

# Test with Samsung
print("\n=== SAMSUNG TEST ===")
r = c.get('/api/products/search?query=Samsung Galaxy S24 256GB')
data = r.json()
print(f"Groups: {data['total_groups']}, Offers: {data['total_offers']}")
