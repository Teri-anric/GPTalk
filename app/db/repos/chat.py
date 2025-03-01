from sqlalchemy import insert, update, or_, exists
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.db import Chat, ChatAISettings, Message
from .base import BaseRepository


class ChatRepository(BaseRepository):
    """
    Repository for handling chat-related database operations.
    """

    async def create_or_update_chat(
        self, chat_id: int, title: str = None, username: str = None
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
                .values(id=chat_id, title=title, username=username)
                .on_conflict_do_update(
                    index_elements=["id"], set_={"title": title, "username": username}
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

    async def update_prompt(self, chat_id: int, prompt: str):
        """
        Update the prompt for a chat.
        """
        async with self.async_session() as session:
            result = await session.execute(
                update(ChatAISettings)
                .where(ChatAISettings.chat_id == chat_id)
                .values(prompt=prompt)
            )
            await session.commit()

            if result.rowcount == 0:
                await session.execute(
                    insert(ChatAISettings).values(chat_id=chat_id, prompt=prompt)
                )
                await session.commit()

    async def update_provider(self, chat_id: int, provider: str):
        """
        Update the provider for a chat.
        """
        async with self.async_session() as session:
            result = await session.execute(
                update(ChatAISettings)
                .where(ChatAISettings.chat_id == chat_id)
                .values(provider=provider)
            )
            await session.commit()

            if result.rowcount == 0:
                await session.execute(
                    insert(ChatAISettings).values(chat_id=chat_id, provider=provider)
                )
                await session.commit()

    async def get_updated_chats(self, last_processed: datetime) -> list[int]:
        """
        Get chats that have been updated after the given timestamp.
        """
        async with self.async_session() as session:
            chats_updated = await session.execute(
                select(Chat.id).where(
                    or_(
                        Chat.updated_at > last_processed,
                        Chat.created_at > last_processed,
                        exists()
                        .select_from(Message)
                        .where(
                            Message.chat_id == Chat.id, Message.created_at > last_processed
                        ),
                    )
                )
            )
            return chats_updated.scalars().all()
