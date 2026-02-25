"""
db - Async database connection management using SQLAlchemy.

Depends: sqlalchemy, asyncpg, config
Consumers: api modules, service layer
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from wenexus.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.app_env == "development",
)
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """Yield an async database session."""
    async with async_session() as session:
        yield session


async def check_db_connection() -> bool:
    """Test database connectivity."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
