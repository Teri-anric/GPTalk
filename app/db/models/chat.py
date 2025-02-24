from sqlalchemy import BigInteger, Column, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .chat_ai_settings import ChatAISettings


class Chat(Base, TimestampMixin):
    """
    Represents a Telegram chat in the database.
    """

    __tablename__ = "chats"

    id = Column(BigInteger, primary_key=True, index=True)
    title = Column(String, nullable=True)
    username = Column(String, nullable=True)

    ai_settings: "ChatAISettings | None" = relationship(
        "ChatAISettings", back_populates="chat"
    )
