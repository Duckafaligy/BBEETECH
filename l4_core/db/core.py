# l4_core/db/core.py

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError

from ..config import settings

Base = declarative_base()

# Switchable DB backend (SQLite for dev, Postgres for prod)
if settings.ENV == "production":
    DATABASE_URL = settings.DATABASE_URL  # from .env
else:
    DATABASE_URL = "sqlite+aiosqlite:///./l4.db"

engine = create_async_engine(
    DATABASE_URL,
    echo=(settings.ENV == "development"),
    future=True,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    """FastAPI dependency for DB access."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise e


async def init_db():
    """Create tables automatically on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def db_healthcheck() -> bool:
    """Simple DB ping for /health endpoint."""
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False
