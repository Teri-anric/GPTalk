"""
Core module for Telegram bot initialization and configuration.
"""

from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError

from app.bot.ai_provider import AIProvider
from app.config import settings

from .handlers import index_router
from .middlewares import DatabaseMiddleware

logger = getLogger(__name__)

bot: Bot | None = None
try:
    bot = Bot(token=settings.bot_token)
except TokenValidationError:
    logger.warning(
        "BOT_TOKEN is not set or invalid, all telegram bot functions will be disabled"
    )

dp = Dispatcher()

# Setup middleware
dp.update.middleware(DatabaseMiddleware())

# Setup routers
dp.include_router(index_router)

# Setup dependencies
dp["ai_provider"] = AIProvider()
