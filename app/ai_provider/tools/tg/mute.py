from ..base import BaseTool

from aiogram import Bot
from aiogram.methods import RestrictChatMember
from aiogram.types import ChatPermissions
from datetime import timedelta

class Mute(BaseTool):
    """
    until_time - mute time in seconds (more than 366 days or less than 30 seconds or not provided - muted forever)
    """
    user_id: int
    until_time: int | None = None

    async def __call__(self, bot: Bot, chat_id: int):
        return await bot(
            RestrictChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                permissions=ChatPermissions(
                    can_send_messages=False,
                ),
                until_date=timedelta(seconds=self.until_time) if self.until_time else None,
            )
        )
