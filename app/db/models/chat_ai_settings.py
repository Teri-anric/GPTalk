from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

from .base import Base

DEFAULT_PROVIDER = "openai:gpt-4o-mini"
DEFAULT_PROMPT = "You are a helpful assistant."
DEFAULT_MESSAGES_LIMIT = 10


class ChatAISettings(Base):
    """
    Chat AI settings model.
    """

    __tablename__ = "chat_ai_settings"

    chat_id = Column(BigInteger, ForeignKey("chats.id"), primary_key=True)

    provider = Column(String, default=DEFAULT_PROVIDER, nullable=False)
    prompt = Column(String, default=DEFAULT_PROMPT, nullable=False)
    messages_limit = Column(Integer, default=DEFAULT_MESSAGES_LIMIT, nullable=False)
