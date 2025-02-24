from aiogram import Bot

from .base import BaseTool


class AnswerTool(BaseTool):
    """
    Answer a message to the user.
    """

    content: str
    reply_to_id: int | None = None

    async def __call__(self, bot: Bot, chat_id: int):
        await bot.send_message(
            chat_id, self.content, reply_to_message_id=self.reply_to_id
        )
