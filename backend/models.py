"""
SQLAlchemy database models for CompareKart.
Defines Product, SearchHistory, and PriceHistory tables.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Index, ForeignKey
)
from sqlalchemy.orm import relationship
from database import Base


class Product(Base):
    """
    Represents a product from any e-commerce platform.
    Stores product information and pricing data.
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(500), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # Amazon, Flipkart, Croma, eBay
    price = Column(Float, nullable=False)
    image_url = Column(Text, nullable=True)
    product_url = Column(Text, nullable=False, unique=False)
    rating = Column(Float, nullable=True)
    rating_count = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_platform_name", "platform", "name"),
        Index("idx_name_platform", "name", "platform"),
    )


class SearchHistory(Base):
    """
    Tracks search queries for analytics and trending.
    Helps understand user search patterns.
    """
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String(255), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    results_count = Column(Integer, nullable=True)
    platform_breakdown = Column(String(500), nullable=True)  # JSON string


class PriceHistory(Base):
    """
    Maintains historical price data for trend analysis.
    Allows tracking price changes over time.
    """
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    price = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    product = relationship("Product", back_populates="price_history")

    __table_args__ = (
        Index("idx_product_recorded", "product_id", "recorded_at"),
    )


class UserAccount(Base):
    """
    User account for app authentication.
    Stores login credentials and profile basics.
    """

    __tablename__ = "user_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(80), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=True)
    email = Column(String(180), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    __table_args__ = (
        Index("idx_user_id_email", "user_id", "email"),
    )
