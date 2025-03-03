import asyncio
import logging

from .chat_processor import BackgroundChatsProcessor
from .scheduled import ScheduledWorker
from app.bot.core import bot

async def main():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    logger.info("Starting worker")
    await asyncio.gather(
        BackgroundChatsProcessor(
            bot=bot,
        ).run(),
        ScheduledWorker(
            assistant_id=bot.id,
        ).run()
    )

if __name__ == "__main__":
    asyncio.run(main())
