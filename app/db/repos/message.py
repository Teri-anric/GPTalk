from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from app.db.models.messages import Message, MessageType

from .base import BaseRepository


class MessageRepository(BaseRepository):
    async def create_message(
        self,
        chat_id: int,
        from_user_id: int,
        type: MessageType,
        content: str,
        send_at: datetime,
        telegram_id: int = None,
        payload: dict = None,
        reply_to_id: int = None,
    ) -> Message:
        """
        Create a new message.

        Args:
            chat_id (int): The ID of the chat.
            from_user_id (int): The ID of the user who sent the message.
            type (MessageType): The type of the message.
            content (str): The content of the message.
            send_at (datetime): The date and time the message was sent.
            payload (dict): Additional data associated with the message.
            reply_to_id (int): The ID of the message being replied to.

        Returns:
            Message: The newly created message.
        """
        # Convert send_at to naive datetime by removing timezone info
        send_at_naive = (
            send_at.replace(tzinfo=None) if send_at.tzinfo is not None else send_at
        )

        result = await self.db.execute(
            insert(Message).values(
                chat_id=chat_id,
                from_user_id=from_user_id,
                content=content,
                type=type,
                send_at=send_at_naive,
                reply_to_id=reply_to_id,
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
            .order_by(Message.send_at.desc())
            .limit(limit)
        )

        return result.scalars().all()
