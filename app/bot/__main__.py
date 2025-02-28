"""
Main entry point for the Telegram bot application before testing.
"""

import logging
import asyncio

from .core import bot, dp


async def main():
    assert bot is not None, (
        "Bot is not initialized, check environment variable BOT_TOKEN"
    )
    logging.info("Starting bot")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())