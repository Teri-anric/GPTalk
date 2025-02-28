"""
Core module for Telegram bot initialization and configuration.
"""

from logging import getLogger

from aiogram import Bot, Dispatcher
from aiogram.utils.token import TokenValidationError

from app.config import settings
from app.db import get_async_session
from app.db import DBReposContext

from .handlers import index_router
from .middlewares import DatabaseMiddleware
from .session_utils import SessionUtils

logger = getLogger(__name__)

bot: Bot | None = None 
db_repo_context = DBReposContext(get_async_session())
try:
    bot = Bot(
        token=settings.bot_token,
        session=SessionUtils(db_repo_context.message),
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
    bot_user = await bot.get_me()
    await db_repo_context.user.create_or_update_user(
        user_id=bot_user.id,
        username=bot_user.username,
        first_name=bot_user.first_name,
        last_name=bot_user.last_name,
    )



# Setup middleware
dp.update.middleware(DatabaseMiddleware())

# Setup routers
dp.include_router(index_router)
