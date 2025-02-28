"""
Middleware for managing context in Telegram bot interactions.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from .repos import ChatRepository, MessageRepository, UserRepository


class DBReposContext:
    """
    Middleware to handle and maintain context during bot interactions.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserRepository(session)
        self.chat = ChatRepository(session)
        self.message = MessageRepository(session)
