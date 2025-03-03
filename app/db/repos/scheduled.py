from datetime import datetime
from uuid import UUID

from sqlalchemy import insert, select, update

from .base import BaseRepository

from ..models import Scheduled


class ScheduledRepo(BaseRepository):
    async def add(self, chat_id: int, message: str, date: datetime):
        async with self.async_session() as session:
            result = await session.execute(
                insert(Scheduled)
                .values(message=message, date=date, chat_id=chat_id)
                .returning(Scheduled)
            )
            await session.commit()
            return result.scalar_one()

    async def get_all_not_done(self, limit: int = 20) -> list[Scheduled]:
        async with self.async_session() as session:
            result = await session.execute(
                select(Scheduled).where(
                    Scheduled.is_done == False, # noqa: E712
                    Scheduled.date < datetime.now(),
                ).limit(limit)
            )
            return result.scalars().all()

    async def marks_as_done(self, ids: list[UUID]):
        async with self.async_session() as session:
            await session.execute(
                update(Scheduled).where(Scheduled.id.in_(ids)).values(is_done=True)
            )
            await session.commit()
