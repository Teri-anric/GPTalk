"""
Core module for Telegram bot initialization and configuration.
"""

from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError

from app.bot.ai_provider import AIProvider
from app.config import settings
from app.db.conn import get_async_session
from app.db.repos import MessageRepository, UserRepository

from .handlers import index_router
from .middlewares import DatabaseMiddleware
from .session_utils import SessionUtils

logger = getLogger(__name__)

bot: Bot | None = None
db_session = get_async_session()
try:
    message_repo = MessageRepository(db_session)
    bot = Bot(
        token=settings.bot_token,
        session=SessionUtils(message_repo),
    )
except TokenValidationError:
    logger.warning(
        "BOT_TOKEN is not set or invalid, all telegram bot functions will be disabled"
    )

dp = Dispatcher()

@dp.startup()
async def startup(bot: Bot):
    await bot.delete_webhook(drop_pending_updates=True)
    # Create bot user if not exists
    user_repo = UserRepository(db_session)
    bot_user = await bot.get_me()
    await user_repo.create_or_update_user(
        user_id=bot_user.id,
        username=bot_user.username,
        first_name=bot_user.first_name,
        last_name=bot_user.last_name,
    )



# Setup middleware
dp.update.middleware(DatabaseMiddleware())

# Setup routers
dp.include_router(index_router)

# Setup dependencies
dp["ai_provider"] = AIProvider()
