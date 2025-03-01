"""
Base repository module.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker


class BaseRepository:
    """
    Base repository for all database repositories.
    """

    def __init__(self, async_session: async_sessionmaker):
        self.async_session = async_session
