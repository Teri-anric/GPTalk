from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, insert
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db import User
from .base import BaseRepository


class UserRepository(BaseRepository):
    """
    Repository for handling user-related database operations.
    """

    async def create_or_update_user(
        self,
        user_id: int,
        first_name: str = None,
        last_name: str = None,
        username: str = None,
    ) -> User:
        """
        Create a new user or update existing user's information using on_conflict_do_update.

        :param user_id: Unique Telegram user ID
        :param first_name: User's first name
        :param last_name: User's last name
        :param username: User's Telegram username
        :return: User object
        """
        async with self.async_session() as session:
            result = await session.execute(
                insert(User)
                    .values(
                    id=user_id,
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
                .on_conflict_do_update(
                    index_elements=["id"],
                    set_={
                        "first_name": first_name,
                        "last_name": last_name,
                        "username": username,
                        "updated_at": datetime.utcnow(),
                    },
                )
                .returning(User)
            )

            await session.commit()
            return result.scalar_one()

    async def get_user_by_id(self, user_id: int) -> User:
        """
        Retrieve a user by their Telegram ID.

        :param user_id: Unique Telegram user ID
        :return: User object or None
        """
        async with self.async_session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
