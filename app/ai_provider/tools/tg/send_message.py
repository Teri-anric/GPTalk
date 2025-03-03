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
    """DON'T use parameters reply_to_message_id and reply_quote, keyboard, inline_keyboard UNLESS ABSOLUTELY NECESSARY. DON'T USE MARKDOWN. USE HTML TAGS:
  <code>, <pre>, <pre><code class="language-python">, <blockquote>, <blockquote expandable>
  <tg-spoiler>, <a href="http://www.example.com/">, <a href="tg://user?id=123456789">, <tg-emoji emoji-id="5368324170671202286">,
  <b>,<strong>, <i>, <em>, <u>, <ins>, <s>, <strike>, <del>, <span class="tg-spoiler">"""

    text: str
    reply_to_message_id: int | None = None
    reply_quote: str | None = None
    keyboard: list[list[str]] | Literal["REMOVE"] | None = None
    inline_keyboard: list[list[Button]] | None = None

    async def __call__(self, bot: Bot, chat_id: int):
        message = await bot(
            SendMessageMethod(
                chat_id=chat_id,
                text=self.text,
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

    def _get_keyboard(self) -> InlineKeyboardMarkup | ReplyKeyboardMarkup | None:
        if self.keyboard == "REMOVE":
            return ReplyKeyboardRemove()
        if self.inline_keyboard and self.inline_keyboard[0]:
            return InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text=button.text, url=button.url)
                        for button in row
                    ]
                    for row in self.inline_keyboard
                ]
            )
        if not self.keyboard or not self.keyboard[0]:
            return None
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=button) for button in row] for row in self.keyboard
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
