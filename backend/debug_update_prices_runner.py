import asyncio
import traceback

from routes.mobile_product_routes import update_prices, UpdatePricesRequest


async def main():
    try:
        result = await update_prices(UpdatePricesRequest(force_refresh=True), {"_id": "debug-user"})
        print(result)
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
