"""
Middleware for database-related operations in the Telegram bot.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message

from app.bot.middlewares.context import DBReposContext
from app.db.conn import get_async_session


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware to manage database connections and sessions for bot interactions.
    """

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with get_async_session() as session:
            data["db"] = DBReposContext(session)
            return await handler(event, data)
