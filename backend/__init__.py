"""
Initialization file for backend package.
Makes services and routes importable.
"""

from database import SessionLocal, init_db, get_db
from models import Product, SearchHistory, PriceHistory, Base

__all__ = [
    "SessionLocal",
    "init_db",
    "get_db",
    "Product",
    "SearchHistory",
    "PriceHistory",
    "Base",
]
