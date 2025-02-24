"""
Middleware for managing context in Telegram bot interactions.
"""

from app.db.conn import AsyncSession
from app.db.repos import ChatRepository, MessageRepository, UserRepository


class DBReposContext:
    """
    Middleware to handle and maintain context during bot interactions.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.user = UserRepository(session)
        self.chat = ChatRepository(session)
        self.message = MessageRepository(session)
