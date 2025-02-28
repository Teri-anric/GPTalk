from aiogram import Bot
from aiogram.methods import SendMessage

from .base import BaseTool


class AnswerTool(BaseTool):
    """
    Answer a message to the user.
    """

    content: str
    reply_to_id: int | None = None

    async def __call__(self, bot: Bot, chat_id: int):
        await bot(
            SendMessage(
                chat_id=chat_id,
                text=self.content,
                reply_to_message_id=self.reply_to_id,
                no_save=True,
            )
        )
