"""
Package for Telegram bot message and command handlers.
"""

from aiogram import Router

from .commands import router as commands_router
from .messages import router as messages_router
from .settings import router as settings_router

index_router = Router()
index_router.include_router(commands_router)
index_router.include_router(settings_router)
index_router.include_router(messages_router)

__all__ = ["index_router"]
