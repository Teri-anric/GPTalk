from datetime import datetime

from aiogram import Bot
from aiogram.client.session.middlewares.base import (
    BaseRequestMiddleware,
    NextRequestMiddlewareType,
)
from aiogram.methods import SendMessage, TelegramMethod
from aiogram.methods.base import Response, TelegramType

from app.db.models.messages import MessageType
from app.db.repos import MessageRepository


class SaveSendMsg(BaseRequestMiddleware):
    """
    Middleware to save sent messages to the database.
    """

    def __init__(self, message_repo: MessageRepository):
        self.message_repo = message_repo

    async def __call__(
        self,
        make_request: NextRequestMiddlewareType[TelegramType],
        bot: Bot,
        method: TelegramMethod[TelegramType],
    ) -> Response[TelegramType]:
        response = await make_request(bot, method)

        if not isinstance(method, SendMessage) or method.model_extra.get("no_save", False):
            return response
        method: SendMessage

        await self.message_repo.create_message(
            telegram_id=response.message_id,

            chat_id=method.chat_id,
            from_user_id=bot.id,
            reply_to_id=method.reply_to_message_id,

            type=MessageType.TEXT,
            content=method.text,
            payload=None,
        )
