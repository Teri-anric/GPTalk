from ..base import BaseTool

from aiogram import Bot
from aiogram.methods import BanChatMember
from datetime import timedelta

class Ban(BaseTool):
    """
    until_time - ban time in seconds (more than 366 days or less than 30 seconds or not provided - banned forever)
    """
    user_id: int
    until_time: int | None = None

    async def __call__(self, bot: Bot, chat_id: int):
        return await bot(
            BanChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                until_date=timedelta(seconds=self.until_time) if self.until_time else None,
            )
        )
