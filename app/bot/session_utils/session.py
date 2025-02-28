from aiogram.client.session.aiohttp import AiohttpSession

from app.db.repos import MessageRepository
from .middlewares import SaveSendMsg

class SessionUtils(AiohttpSession):
    def __init__(self, message_repo: MessageRepository, proxy: str | None = None, limit: int = 100, **kwargs) -> None:
        super().__init__(proxy=proxy, limit=limit, **kwargs)
        self._message_repo = message_repo
        self.middleware.register(SaveSendMsg(self._message_repo))
