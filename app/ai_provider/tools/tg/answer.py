from aiogram import Bot
from aiogram.methods import SendMessage

from ..base import BaseTool


class Answer(BaseTool):
    content: str

    async def __call__(self, bot: Bot, chat_id: int):
        message = await bot(
            SendMessage(
                chat_id=chat_id,
                text=self.content,
                no_save=True,
            )
        )
        return {"message_id": message.message_id}