import asyncio
import logging

from app.worker.worker import BackgroundChatsProcessor
from app.bot.core import bot


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(BackgroundChatsProcessor(
        bot=bot,
    ).run())
