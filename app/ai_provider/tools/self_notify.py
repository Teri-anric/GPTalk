import asyncio
from datetime import datetime, timedelta
import time
import logging

from .base import BaseTool

from app.db import DBReposContext, MessageType

logger = logging.getLogger(__name__)


class SelfNotify(BaseTool):
    """
    You can use this tool to notify yourself about something.
    :param message: Message to notify yourself about.
    :param date: Date in isoformat or delay in seconds.
    """
    message: str
    date: str | int

    async def _get_sleep_time(self) -> int:
        if isinstance(self.date, str):  
            return max(1, datetime.fromisoformat(self.date).timestamp() - time.time())
        return self.date
    
    async def _get_date(self) -> datetime:
        if isinstance(self.date, str):
            return datetime.fromisoformat(self.date)
        return datetime.now() + timedelta(seconds=self.date)

    async def notify_task(self, db: DBReposContext, chat_id: int, assistant_id: int):
        sleep_time = await self._get_sleep_time()
        logger.info(f"Creating task to notify {chat_id} at {self.date} in {sleep_time} seconds")
        await asyncio.sleep(sleep_time)
        await db.message.create_message(
            chat_id=chat_id,
            from_user_id=assistant_id,
            type=MessageType.TEXT,
            content=self.message,
        )

    async def __call__(self, db: DBReposContext, chat_id: int, assistant_id: int):
        asyncio.create_task(self.notify_task(db, chat_id, assistant_id))
        return f"Scheduled at {await self._get_date()}"
