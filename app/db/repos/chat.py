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
        await self.db.execute(
            pg_insert(Chat)
            .values(id=chat_id, title=title, username=username)
            .on_conflict_do_update(
                index_elements=["id"], set_={"title": title, "username": username}
            )
        )

        await self.db.commit()
        return await self.get_chat_by_id(chat_id)

    async def get_chat_by_id(self, chat_id: int) -> Chat:
        """
        Retrieve a chat by its ID.

        :param chat_id: Unique chat ID
        :return: Chat object or None
        """
        result = await self.db.execute(
            select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.ai_settings))
        )
        return result.scalar_one_or_none()

    async def update_prompt(self, chat_id: int, prompt: str):
        """
        Update the prompt for a chat.
        """
        result = await self.db.execute(
            update(ChatAISettings)
            .where(ChatAISettings.chat_id == chat_id)
            .values(prompt=prompt)
        )
        await self.db.commit()
        
        if result.rowcount == 0:
            await self.db.execute(
                insert(ChatAISettings).values(chat_id=chat_id, prompt=prompt)
            )
            await self.db.commit()

    async def update_provider(self, chat_id: int, provider: str):
        """
        Update the provider for a chat.
        """
        result = await self.db.execute(
            update(ChatAISettings)
            .where(ChatAISettings.chat_id == chat_id)
            .values(provider=provider)
        )
        await self.db.commit()

        if result.rowcount == 0:
            await self.db.execute(
                insert(ChatAISettings).values(chat_id=chat_id, provider=provider)
            )
            await self.db.commit()

    async def get_updated_chats(self, last_processed: datetime) -> list[int]:
        """
        Get chats that have been updated after the given timestamp.
        """
        chats_updated = await self.db.execute(
            select(Chat.id).where(
                or_(
                    Chat.updated_at > last_processed,
                    Chat.created_at > last_processed,
                    exists().select_from(Message).where(
                        Message.chat_id == Chat.id,
                        Message.created_at > last_processed
                    )
                )
            )
        )
        return chats_updated.scalars().all()
