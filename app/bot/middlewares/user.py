"""
Middleware for handling user-related operations in the Telegram bot.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from .context import DBReposContext


class UserMiddleware(BaseMiddleware):
    """
    Middleware to process and manage user-related context in bot interactions.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user = event.from_user
        db: DBReposContext = data["db"]

        data["db_user"] = await db.user.create_or_update_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

        return await handler(event, data)
