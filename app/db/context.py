"""
Middleware for managing context in Telegram bot interactions.
"""

from sqlalchemy.ext.asyncio import async_sessionmaker

from .repos import ChatRepository, MessageRepository, UserRepository
from .conn import get_async_session


class DBReposContext:
    """
    Middleware to handle and maintain context during bot interactions.
    """

    def __init__(self, session_maker: async_sessionmaker | None = None):
        self.async_session = session_maker or get_async_session()
        self.user = UserRepository(self.async_session)
        self.chat = ChatRepository(self.async_session)
        self.message = MessageRepository(self.async_session)
