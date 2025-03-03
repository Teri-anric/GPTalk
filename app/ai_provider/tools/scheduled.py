from datetime import datetime, timedelta
import logging

from .base import BaseTool

from app.db import DBReposContext

logger = logging.getLogger(__name__)


class Scheduled(BaseTool):
    """
    You can use this tool to notify yourself about something.(This notify don't visible for users)
    :param message: Message to notify yourself.
    :param date: Date in isoformat or delay in seconds.
    """
    message: str
    date: str | int

    async def _get_date(self) -> datetime:
        if isinstance(self.date, str):
            return datetime.fromisoformat(self.date)
        return datetime.now() + timedelta(seconds=self.date)

    async def __call__(self, db: DBReposContext, chat_id: int, assistant_id: int):
        await db.scheduled.add(chat_id, self.message, await self._get_date())
        return f"Scheduled at {await self._get_date()}"
