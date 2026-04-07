"""Quick test of grouped comparison."""
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, 'backend')
from main import app

c = TestClient(app)
r = c.get('/api/products/search?query=samsung galaxy s24')
data = r.json()

print(f"Status: {r.status_code}")
print(f"Total groups: {data['total_groups']}")
print(f"Total offers: {data['total_offers']}")
print("\nTop groups:")
for g in data['product_groups'][:5]:
    print(f"  {g['product_name'][:60]}")
    print(f"    Offers: {g['offer_count']}, Best: ${g['best_price']:.2f}, Avg: ${g['average_price']:.2f}")
