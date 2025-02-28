from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

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
        reply_to_id: int | None = None,
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
            reply_to_id (int): The ID of the message being replied to.

        Returns:
            Message: The newly created message.
        """
        result = await self.db.execute(
            insert(Message).values(
                chat_id=chat_id,
                from_user_id=from_user_id,
                type=type,
                content=content or "",
                reply_to_id=reply_to_id,
                telegram_id=telegram_id,
                payload=payload,
            ).returning(Message)
        )

        await self.db.commit()
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
        result = await self.db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        return result.scalars().all()
