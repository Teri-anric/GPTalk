from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
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
    from .chats import Chat
    from .users import User


class MessageType(PyEnum):
    TEXT = "text"
    TOOL_CALL = "tool_call"
    # IMAGE = "image"
    # AUDIO = "audio"
    # VIDEO = "video"
    # DOCUMENT = "document"
    # LOCATION = "location"


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: int = Column(BigInteger, primary_key=True)
    type: MessageType = Column(
        Enum(MessageType), nullable=False, default=MessageType.TEXT
    )
    content: str = Column(String, default="", nullable=False)
    payload: dict = Column(JSON, nullable=True, default=None)
    send_at: datetime = Column(DateTime)

    reply_to_id: int = Column(BigInteger, ForeignKey("messages.id"), nullable=True)
    from_user_id: int = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    chat_id: int = Column(BigInteger, ForeignKey("chats.id"), nullable=False)

    from_user: "User" = relationship("User")
    chat: "Chat" = relationship("Chat")
    reply_to: "Message" = relationship("Message", back_populates="reply_to")
