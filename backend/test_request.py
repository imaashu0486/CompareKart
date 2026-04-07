"""Test requests to running server."""
import asyncio
import httpx
import time

async def test():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/health", timeout=5)
            print(f"Status: {response.status_code}")
            print(f"Body: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("Waiting for server to be ready...")
    time.sleep(4)
    print("Making request...")
    asyncio.run(test())
    print("Request completed")
