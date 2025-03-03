from sqlalchemy import insert, update, or_, not_
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.db import Chat, ChatAISettings, Message, MessageType, ChatType
from .base import BaseRepository

UNSET = object()

class ChatRepository(BaseRepository):
    """
    Repository for handling chat-related database operations.
    """

    async def create_or_update_chat(
        self, chat_id: int, title: str = None, username: str = None, type: ChatType = None
    ) -> Chat:
        """
        Create a new chat or update existing chat's information using on_conflict_do_update.

        :param chat_id: Unique Telegram chat ID
        :param title: Chat title
        :param username: Chat username

        :return: Chat object
        """
        async with self.async_session() as session:
            await session.execute(
                pg_insert(Chat)
                .values(id=chat_id, title=title, username=username, type=type)
                .on_conflict_do_update(
                    index_elements=["id"], set_={"title": title, "username": username, "type": type}
                )
            )
            await session.commit()
            return await self.get_chat_by_id(chat_id)

    async def get_chat_by_id(self, chat_id: int) -> Chat:
        """
        Retrieve a chat by its ID.

        :param chat_id: Unique chat ID
        :return: Chat object or None
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Chat)
                .where(Chat.id == chat_id)
                .options(selectinload(Chat.ai_settings))
            )
            chat = result.scalar_one_or_none()
            # Create a new ChatAISettings if it doesn't exist
            if chat and chat.ai_settings is None:
                chat.ai_settings = ChatAISettings(chat_id=chat_id)
                await session.commit()
            return chat


    async def update_ai_settings(
        self,
        chat_id: int,
        prompt: str = UNSET,
        provider: str = UNSET,
        messages_context_limit: int = UNSET,
        max_not_response_time: int | None = UNSET,
        min_delay_between_messages: int | None = UNSET,
    ):
        """
        Update the AI settings for a chat.
        """
        async with self.async_session() as session:
            data = {}
            if prompt is not UNSET:
                data["prompt"] = prompt
            if provider is not UNSET:
                data["provider"] = provider
            if messages_context_limit is not UNSET:
                data["messages_context_limit"] = messages_context_limit
            if max_not_response_time is not UNSET:
                data["max_not_response_time"] = max_not_response_time
            if min_delay_between_messages is not UNSET:
                data["min_delay_between_messages"] = min_delay_between_messages
            
            result = await session.execute(
                update(ChatAISettings)
                .where(ChatAISettings.chat_id == chat_id)
                .values(
                    **data
                )
            )
            await session.commit()

            if result.rowcount == 0:
                await session.execute(
                    insert(ChatAISettings).values(
                        chat_id=chat_id,
                        **data
                    )
                )
                await session.commit()

    
    async def get_updated_chats_settings(self, last_processed: datetime) -> list[ChatAISettings]:
        """
        Get chats that have been updated after the given timestamp.
        """
        async with self.async_session() as session:
            chats_updated = await session.execute(
                select(ChatAISettings).where(
                    or_(
                        ChatAISettings.updated_at > last_processed,
                        ChatAISettings.created_at > last_processed,
                    )
                )
            )
            return chats_updated.scalars().all()

    async def get_awaible_new_messages_in_chats(self, last_processed: datetime, except_types: list[MessageType] | None = None) -> list[int]:
        """
        Get chats that have new messages after the given timestamp.
        """
        async with self.async_session() as session:
            chats_updated = await session.execute(
                select(Message.chat_id).where(
                    Message.created_at > last_processed,
                    not_(Message.type.in_(except_types)) if except_types else True,
                ).group_by(Message.chat_id)
            )
            return chats_updated.scalars().all()
