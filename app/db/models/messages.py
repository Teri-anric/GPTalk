from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
import uuid
from sqlalchemy import (
    BigInteger,
    UUID,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    JSON,
    String,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .chat import Chat
    from .user import User


class MessageType(PyEnum):
    TEXT = "text"
    TOOL_CALLS = "tool_calls"
    AI_REFLECTION = "ai_reflection"
    # TRIGGER = "trigger"
    # IMAGE = "image"
    # AUDIO = "audio"
    # VIDEO = "video"
    # DOCUMENT = "document"
    # LOCATION = "location"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: int = Column(UUID, primary_key=True, default=uuid.uuid4)

    type: MessageType = Column(
        Enum(MessageType), nullable=False, default=MessageType.TEXT
    )
    content: str = Column(String, default="", nullable=False)
    payload: dict = Column(JSON, nullable=True, default=None)
    send_at: datetime = Column(DateTime)

    reply_to_id: int = Column(BigInteger, nullable=True)
    from_user_id: int = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    chat_id: int = Column(BigInteger, ForeignKey("chats.id"), nullable=False)

    telegram_id: int = Column(BigInteger, nullable=True)

    from_user: "User" = relationship("User")
    chat: "Chat" = relationship("Chat")
    # reply_to: "Message" = relationship("Message", primaryjoin="Message.reply_to_id == Message.id")
