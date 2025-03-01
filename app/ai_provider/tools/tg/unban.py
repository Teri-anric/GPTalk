from ..base import BaseTool

from aiogram import Bot
from aiogram.methods import UnbanChatMember


class Unban(BaseTool):
    user_id: int

    async def __call__(self, bot: Bot, chat_id: int):
        return await bot(
            UnbanChatMember(chat_id=chat_id, user_id=self.user_id)
        )
