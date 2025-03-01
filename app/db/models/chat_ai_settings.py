from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String

from .base import Base

DEFAULT_PROVIDER = "openai:gpt-4o-mini"
DEFAULT_PROMPT = "You are a helpful assistant."
DEFAULT_MESSAGES_CONTEXT_LIMIT = 10
DEFAULT_MAX_NOT_RESPONSE_TIME = None
DEFAULT_MIN_DELAY_BETWEEN_MESSAGES = 10


class ChatAISettings(Base):
    """
    Chat AI settings model.
    """

    __tablename__ = "chat_ai_settings"

    chat_id = Column(BigInteger, ForeignKey("chats.id"), primary_key=True)

    provider = Column(String, default=DEFAULT_PROVIDER, nullable=False)
    prompt = Column(String, default=DEFAULT_PROMPT, nullable=False)
    messages_context_limit = Column(
        Integer, default=DEFAULT_MESSAGES_CONTEXT_LIMIT, nullable=False
    )
    max_not_response_time = Column(
        Integer, default=DEFAULT_MAX_NOT_RESPONSE_TIME, nullable=True
    )
    min_delay_between_messages = Column(
        Integer, default=DEFAULT_MIN_DELAY_BETWEEN_MESSAGES, nullable=True
    )
