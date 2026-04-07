import os
from typing import Optional
import certifi
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_database() -> AsyncIOMotorDatabase:
    global _client, _db
    if _db is None:
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        db_name = os.getenv("MONGO_DB_NAME", "smart_price_comparator")
        client_kwargs = {
            "serverSelectionTimeoutMS": 15000,
            "connectTimeoutMS": 15000,
            "socketTimeoutMS": 15000,
        }
        if mongo_uri.startswith("mongodb+srv://"):
            client_kwargs["tls"] = True
            client_kwargs["tlsCAFile"] = certifi.where()
        _client = AsyncIOMotorClient(mongo_uri, **client_kwargs)
        _db = _client[db_name]
    return _db


async def init_mongo_indexes() -> None:
    db = get_database()
    try:
        await db.products.create_index([("category", 1), ("brand", 1), ("model", 1)])
        await db.products.create_index([("variant_name", "text"), ("brand", "text"), ("model", "text")])
        await db.users.create_index("email", unique=True)
    except Exception:
        # Allow API startup even when MongoDB is temporarily unavailable.
        return


async def close_mongo() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
    _client = None
    _db = None
