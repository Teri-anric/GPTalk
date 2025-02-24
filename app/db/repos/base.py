"""
Base repository module.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """
    Base repository for all database repositories.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
