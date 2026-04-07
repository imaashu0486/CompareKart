"""
Database configuration and connection setup.
Supports both SQLite (development) and PostgreSQL (production).
"""

import os
from typing import Optional, Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "sqlite:///./comparekart.db"  # Default SQLite for development
)

# Create engine based on database type
if "postgresql" in DATABASE_URL:
    # PostgreSQL production configuration
    engine: Engine = create_engine(
        DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )
else:
    # SQLite development configuration
    engine: Engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI to get database session.
    Usage: In route handler, add: db: Session = Depends(get_db)
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def drop_all_tables() -> None:
    """Drop all tables (use with caution)."""
    Base.metadata.drop_all(bind=engine)
