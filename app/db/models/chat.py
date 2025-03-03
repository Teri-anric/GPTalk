from enum import Enum as PyEnum

from sqlalchemy import BigInteger, Column, String, Enum
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .chat_ai_settings import ChatAISettings

class ChatType(PyEnum):
    PRIVATE = "private"
    GROUP = "group"
    SUPERGROUP = "supergroup"
    CHANNEL = "channel"

class Chat(Base, TimestampMixin):
    """
    Represents a Telegram chat in the database.
    """

    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, nullable=True)
    username = Column(String, nullable=True)
    type = Column(Enum(ChatType), nullable=False)

    ai_settings: "ChatAISettings | None" = relationship(
        "ChatAISettings"
    )
