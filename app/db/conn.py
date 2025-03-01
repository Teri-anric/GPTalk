"""
Database connection module.
"""

from functools import cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings


def get_async_engine(url: str = settings.database.url) -> AsyncEngine:
    """
    Get an async engine for the database.
    """
    return create_async_engine(url)



def get_async_session(engine: AsyncEngine | None = None) -> async_sessionmaker:
    """
    Get an async session for the database.
    """
    if engine is None:
        engine = get_async_engine()

    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    return async_session