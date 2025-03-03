from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from app.db import Message, MessageType

from .base import BaseRepository


class MessageRepository(BaseRepository):
    async def create_message(
        self,
        chat_id: int,
        type: MessageType,
        from_user_id: int | None = None,
        content: str = None,
        telegram_id: int | None = None,
        payload: dict | None = None,
    ) -> Message:
        """
        Create a new message.

        Args:
            chat_id (int): The ID of the chat.
            type (MessageType): The type of the message.
            from_user_id (int): The ID of the user who sent the message.
            content (str): The content of the message.
            telegram_id (int): The ID of the message in Telegram.
            payload (dict): Additional data associated with the message.

        Returns:
            Message: The newly created message.
        """
        async with self.async_session() as session:
            result = await session.execute(
                insert(Message).values(
                    chat_id=chat_id,
                    from_user_id=from_user_id,
                    type=type,
                    content=content or "",
                    telegram_id=telegram_id,
                    payload=payload,
                ).returning(Message)
            )

            await session.commit()
            return result.scalar_one()

    async def get_last_messages(self, chat_id: int, limit: int = 10) -> list[Message]:
        """
        Get the last messages from a chat.

        Args:
            chat_id (int): The ID of the chat.
            limit (int): The maximum number of messages to retrieve.

        Returns:
            list[Message]: A list of the last messages from the chat.
        """
        async with self.async_session() as session:
            result = await session.execute(
                select(Message)
                .where(Message.chat_id == chat_id)
                .order_by(Message.created_at.desc())
                .options(selectinload(Message.from_user))
                .limit(limit)
            )

            return result.scalars().all()
