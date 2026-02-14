# l4_core/db/core.py

"""
DB Core (L4+)
-------------
Centralized database configuration for the AI OS.

Features:
  - Async SQLAlchemy engine + session factory
  - Environment-aware backend switching (SQLite dev → Postgres prod)
  - Safe session dependency for FastAPI
  - Healthcheck endpoint support
  - Future-proof for migrations, sharding, and multi-tenant DBs
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from l4_core.config import settings



# ---------------------------------------------------------
# BASE MODEL
# ---------------------------------------------------------
Base = declarative_base()


# ---------------------------------------------------------
# DATABASE URL SELECTION
# ---------------------------------------------------------
if settings.ENV == "production":
    # Production uses the configured Postgres URL
    DATABASE_URL = settings.DATABASE_URL
else:
    # Development uses local SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./l4.db"


# ---------------------------------------------------------
# ENGINE
# ---------------------------------------------------------
engine = create_async_engine(
    DATABASE_URL,
    echo=(settings.ENV == "development"),
    future=True,
    pool_pre_ping=True,
)


# ---------------------------------------------------------
# SESSION FACTORY
# ---------------------------------------------------------
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


# ---------------------------------------------------------
# FASTAPI DEPENDENCY
# ---------------------------------------------------------
async def get_db():
    """
    FastAPI dependency for DB access.
    Ensures rollback on SQLAlchemy errors.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError:
            await session.rollback()
            raise


# ---------------------------------------------------------
# INITIALIZATION
# ---------------------------------------------------------
async def init_db():
    """
    Create tables automatically on startup.
    Future: migrations, versioning, schema diffs.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---------------------------------------------------------
# HEALTHCHECK
# ---------------------------------------------------------
async def db_healthcheck() -> bool:
    """
    Simple DB ping for /health endpoint.
    Uses a safe text() query for compatibility.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
