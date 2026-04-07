"""
Simple test script to verify scrapers are working.
This makes HTTP requests to the running backend.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_search():
    """Test the search endpoint."""
    print("\n" + "="*80)
    print("Testing Search Endpoint")
    print("="*80)
    
    query = "laptop"
    url = f"{BASE_URL}/api/products/search?query={query}&limit=10"
    
    print(f"\nRequesting: {url}")
    print("Please wait... (15-30 seconds expected on first request)")
    
    start_time = time.time()
    
    try:
        response = requests.get(url, timeout=120)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Response received in {elapsed:.1f} seconds")
        print(f"Status Code: {response.status_code}")
        
        data = response.json()
        
        print(f"\nResults:")
        print(f"  Total products: {len(data.get('results', []))}")
        print(f"  Platforms: {data.get('platforms', [])}")
        
        if data.get('results'):
            print(f"\nFirst 3 products:")
            for i, product in enumerate(data['results'][:3], 1):
                print(f"\n  Product {i}:")
                print(f"    Name: {product.get('name', 'N/A')[:50]}...")
                print(f"    Platform: {product.get('platform', 'N/A')}")
                print(f"    Price: ${product.get('price', 'N/A')}")
                print(f"    Rating: {product.get('rating', 'N/A')}/5")
        else:
            print("\n⚠️  No products returned")
            print(f"Full response: {json.dumps(data, indent=2)[:500]}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (backend is slow)")
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - is backend running?")
        print(f"   Try: python main.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_compare():
    """Test the compare endpoint."""
    print("\n" + "="*80)
    print("Testing Compare Endpoint")
    print("="*80)
    
    query = "iphone"
    url = f"{BASE_URL}/api/products/compare?query={query}&limit=10"
    
    print(f"\nRequesting: {url}")
    
    try:
        response = requests.get(url, timeout=120)
        
        print(f"Status Code: {response.status_code}")
        data = response.json()
        
        print(f"\nComparison Results:")
        print(f"  Total products: {len(data.get('results', []))}")
        print(f"  Platforms: {data.get('platforms', [])}")
        
        if data.get('stats'):
            stats = data['stats']
            print(f"\nPrice Statistics:")
            print(f"  Cheapest: ${stats.get('min_price', 'N/A')}")
            print(f"  Most Expensive: ${stats.get('max_price', 'N/A')}")
            print(f"  Average: ${stats.get('avg_price', 'N/A'):.2f}")
            
    except Exception as e:
        print(f"Error: {str(e)}")


def test_api_docs():
    """Check if API docs are accessible."""
    print("\n" + "="*80)
    print("Testing API Documentation")
    print("="*80)
    
    url = f"{BASE_URL}/docs"
    
    print(f"\nAPI Documentation: {url}")
    print("Open this in your browser to explore endpoints and test them interactively")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("✅ API docs are accessible")
        else:
            print(f"⚠️  API docs returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("CompareKart Backend - API Test Suite")
    print("="*80)
    print("\nThis script tests the CompareKart backend API")
    print("Ensure the backend is running: python main.py")
    
    test_api_docs()
    test_search()
    test_compare()
    
    print("\n" + "="*80)
    print("Test suite complete!")
    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
