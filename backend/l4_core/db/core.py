# l4_core/db/core.py

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base

from ..config import settings

# Base ORM class
Base = declarative_base()

# Database URL (SQLite for now, upgradeable to Postgres later)
DATABASE_URL = "sqlite+aiosqlite:///./l4.db"

# Async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=(settings.ENV == "development"),
    future=True,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    """Dependency for FastAPI routes."""
    async with AsyncSessionLocal() as session:
        yield session
