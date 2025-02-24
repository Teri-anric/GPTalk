"""
Middleware for handling chat-related operations in the Telegram bot.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


class ChatMiddleware(BaseMiddleware):
    """
    Middleware to process and manage chat-related context in bot interactions.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        """
        Process chat information and add it to the context.

        :param handler: Next handler in the middleware chain
        :param event: Incoming message event
        :param data: Context data dictionary
        :return: Result of the next handler
        """
        chat = event.chat
        db = data["db"]

        data["db_chat"] = await db.chat.create_or_update_chat(
            id=chat.id,
            title=chat.title,
            username=chat.username,
        )

        return await handler(event, data)
