from sqlalchemy import BigInteger, Column, ForeignKey, String

from .base import Base


class ChatAISettings(Base):
    """
    Chat AI settings model.
    """

    __tablename__ = "chat_ai_settings"

    chat_id = Column(BigInteger, ForeignKey("chats.id"), primary_key=True)

    provider = Column(String, nullable=True)
    prompt = Column(String, nullable=True)
