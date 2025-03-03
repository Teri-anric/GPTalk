from typing import Literal

from aiogram import Bot
from aiogram.methods import SendMessage

from ..base import BaseTool


class Answer(BaseTool):
    """
    Send a message to a chat.
    HTML style use tags: <b>,<strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>, <span class="tg-spoiler">, 
        <tg-spoiler>, <a href="http://www.example.com/">, <a href="tg://user?id=123456789">, <tg-emoji emoji-id="5368324170671202286">, 
        <code>, <pre>, <pre><code class="language-python">, <blockquote>, <blockquote expandable>
    """

    content: str

    async def __call__(self, bot: Bot, chat_id: int):
        message = await bot(
            SendMessage(
                chat_id=chat_id,
                text=self.content,
                no_save=True,
                parse_mode="HTML",
            )
        )
        return {"message_id": message.message_id}
