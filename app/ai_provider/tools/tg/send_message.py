from pydantic import BaseModel
from typing import Literal

from aiogram import Bot
from aiogram.methods import SendMessage as SendMessageMethod
from aiogram.types import (
    ReplyParameters,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)

from ..base import BaseTool


class Button(BaseModel):
    text: str
    url: str | None = None


class SendMessage(BaseTool):
    """
    Send a message to a chat.
    HTML style use tags: <b>,<strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>, <span class="tg-spoiler">,
        <tg-spoiler>, <a href="http://www.example.com/">, <a href="tg://user?id=123456789">, <tg-emoji emoji-id="5368324170671202286">,
        <code>, <pre>, <pre><code class="language-python">, <blockquote>, <blockquote expandable>
    Do not use reply_to_message_id and reply_quote, keyboard unless absolutely necessary.
    """

    text: str
    reply_to_message_id: int | None = None
    reply_quote: str | None = None
    keyboard: list[list[Button]] | list[list[str]] | Literal["REMOVE"] = None

    async def __call__(self, bot: Bot, chat_id: int):
        message = await bot(
            SendMessageMethod(
                chat_id=chat_id,
                text=self.text,
                no_save=True,
                parse_mode="HTML",
                reply_parameters=ReplyParameters(
                    message_id=self.reply_to_message_id,
                    quote=self.reply_quote,
                    quote_parse_mode="HTML",
                ),
                reply_markup=self._get_keyboard(),
            )
        )
        return {"message_id": message.message_id}

    def _get_keyboard(self) -> InlineKeyboardMarkup | None:
        if self.keyboard == "REMOVE":
            return ReplyKeyboardRemove()
        if not self.buttons or not self.buttons[0]:
            return None
        if isinstance(self.buttons[0][0], str):
            return ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text=button.text, url=button.url) for button in row]
                    for row in self.buttons
                ]
            )
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=button.text, url=button.url)
                    for button in row
                ]
                for row in self.buttons
            ]
        )
