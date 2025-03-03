"""
Middleware for database-related operations in the Telegram bot.
"""

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, html
from aiogram.dispatcher.flags import extract_flags
from aiogram.types import (
    TelegramObject,
    Chat as TelegramChat,
    User as TelegramUser,
    Message as TelegramMessage,
)
from aiogram.fsm.middleware import EVENT_CONTEXT_KEY, EventContext

from app.db import DBReposContext
from app.db import Chat as DBChat, User as DBUser, Message as DBMessage
from app.db import MessageType, ChatType


class DatabaseMiddleware(BaseMiddleware):
    """
    Middleware to manage database connections and sessions for bot interactions.
    """

    async def _resolve_db_chat(
        self, db: DBReposContext, chat: TelegramChat | None
    ) -> DBChat | None:
        if chat is None:
            return None
        return await db.chat.create_or_update_chat(
            chat_id=chat.id,
            title=chat.full_name,
            username=chat.username,
            type=ChatType(chat.type),
        )

    async def _resolve_db_user(
        self, db: DBReposContext, user: TelegramUser | None
    ) -> DBUser | None:
        if user is None:
            return None
        return await db.user.create_or_update_user(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
        )

    async def _resolve_db_message(
        self,
        db: DBReposContext,
        message: TelegramMessage | None,
        chat_id: int = None,
        user_id: int = None,
    ) -> DBMessage | None:
        if message is None or message.html_text is None:
            return None

        payload = {}

        if message.reply_to_message is not None:
            payload.setdefault("reply_to", {}).update({
                "id": message.reply_to_message.message_id,
                "type": "reply",
                "content": message.reply_to_message.html_text,
            })
        if message.quote:
            payload.setdefault("reply_to", {}).update({
                "type": "quote",
                "content": html.unparse(message.quote.text, message.quote.entities),
            })
        if message.external_reply:
            payload.setdefault("reply_to", {}).update({
                "id": message.external_reply.message_id,
                "type": "external",
                "chat_id": message.external_reply.chat.id if message.external_reply.chat else None,
            })
        if message.forward_origin:
            payload["is_forwarded"] = True
    
        return await db.message.create_message(
            chat_id=chat_id,
            from_user_id=user_id,
            type=MessageType.TEXT,
            payload=payload,
            content=message.html_text,
            telegram_id=message.message_id,
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        event_context: EventContext | None = data.get(EVENT_CONTEXT_KEY)

        db = DBReposContext()

        data["db"] = db
        if event_context is not None:
            data["db_chat"] = await self._resolve_db_chat(db, event_context.chat)
            data["db_user"] = await self._resolve_db_user(db, event_context.user)
        if event.message is not None and "not_saved" not in extract_flags(handler):
            data["db_message"] = await self._resolve_db_message(
                db,
                event.message,
                chat_id=event_context.chat_id,
                user_id=event_context.user_id,
            )
        return await handler(event, data)
