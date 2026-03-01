"""
db - Async database connection management using SQLAlchemy.

Engine and session factory are created lazily on first use so that
importing this module without a DATABASE_URL (e.g. in CI unit tests)
does not raise an error.

Depends: sqlalchemy, asyncpg, config
Consumers: api modules, service layer
"""

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from wenexus.config import settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=settings.app_env == "development",
        )
    return _engine


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            _get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session."""
    async with _get_session_factory()() as session:
        yield session


async def check_db_connection() -> bool:
    """Test database connectivity."""
    if not settings.database_url:
        return False
    try:
        async with _get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
