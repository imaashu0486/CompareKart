"""Simple HTTP client to test backend."""
import requests
import time
import sys

def test_server():
    base_url = "http://localhost:8000"
    
    # Wait for server to start
    time.sleep(5)
    
    print("Testing health endpoint...")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Health request failed: {e}")
        return False
    
    print("\nTesting root endpoint...")
    try:
        r = requests.get(f"{base_url}/", timeout=5)
        print(f"Root: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Root request failed: {e}")
        return False
    
    print("\nTesting search endpoint...")
    try:
        r = requests.get(f"{base_url}/api/products/search?query=phone&limit=2", timeout=30)
        print(f"Search: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Found {data['total_results']} products")
            if data.get('products'):
                print(f"First product: {data['products'][0]['title']}")
    except Exception as e:
        print(f"Search request failed: {e}")
        return False
    
    print("\nServer is working correctly!")
    return True

if __name__ == "__main__":
    sys.exit(0 if test_server() else 1)
