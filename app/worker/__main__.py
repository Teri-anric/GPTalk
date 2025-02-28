import asyncio
import logging

from app.worker.worker import BackgroundChatsProcessor
from app.bot.core import bot, db_repo_context


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(BackgroundChatsProcessor(
        db=db_repo_context,
        bot=bot,
    ).run())
