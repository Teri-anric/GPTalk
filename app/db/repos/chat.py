from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.future import select
from sqlalchemy.orm import relationship, selectinload

from app.db.models import Chat, ChatAISettings
from app.db.repos.base import BaseRepository


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
        # Prepare the insert statement with on_conflict_do_update
        result = await self.db.execute(
            insert(Chat)
            .values(id=chat_id, title=title, username=username)
            .on_conflict_do_update(
                index_elements=["chat_id"], set_={"title": title, "username": username}
            )
            .returning(select(Chat).options(selectinload(Chat.ai_settings)))
        )

        await self.db.commit()
        return result.scalar_one()

    async def get_chat_by_id(self, chat_id: int) -> Chat:
        """
        Retrieve a chat by its ID.

        :param chat_id: Unique chat ID
        :return: Chat object or None
        """
        result = await self.db.execute(select(Chat).where(Chat.id == chat_id))
        return result.scalar_one_or_none()

    async def update_prompt(self, chat_id: int, prompt: str):
        """
        Update the prompt for a chat.
        """
        await self.db.execute(
            insert(ChatAISettings).values(chat_id=chat_id, prompt=prompt)
            .on_conflict_do_update(
                index_elements=["chat_id"], set_={"prompt": prompt}
            )
        )
        await self.db.commit()
