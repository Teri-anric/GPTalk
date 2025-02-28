import time
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from .logger import logger

from aiogram import Bot

from app.db import DBReposContext
from app.ai_provider import AIProvider
from app.worker.ai_processor import AIProcessor


DEFAULT_MAX_DELAY = 60 * 60 * 1  # 1 hour
DEFAULT_MIN_DELAY = 1  # 10 seconds


@dataclass
class ChatProcessInfo:
    chat_id: int
    last_processed: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)

    def is_ready_to_process(self) -> bool:
        is_ready = (time.time() - self.last_processed) > DEFAULT_MAX_DELAY
        if self.last_updated >= self.last_processed:
            is_ready = True
        if is_ready:
            self.last_processed = time.time()
        return is_ready

    def set_last_updated(self, last_updated: float):
        self.last_updated = last_updated


class BackgroundChatsProcessor:
    """
    Background task for processing chats.
    """

    def __init__(
        self, db: DBReposContext, bot: Bot, **workflow_data
    ):
        self.db = db
        self.bot = bot
        self.ai_provider = AIProvider()
        self.workflow_data = workflow_data

        self.ai_processor = AIProcessor(
            self.db, self.bot, self.ai_provider, **self.workflow_data
        )

        self.chats: dict[int, ChatProcessInfo] = {}

    async def _process_chats(self):
        tasks = []
        while True:
            last_processed = time.time()
            logger.debug(f"Start processing {len(self.chats)} chats")
            for chat_id in list(self.chats.keys()):
                chat_info = self.chats[chat_id]
                if not chat_info.is_ready_to_process():
                    logger.debug(f"Chat {chat_id} is not ready to process")
                    continue
                logger.info(f"Adding chat to process: {chat_id}") 
                tasks.append(asyncio.create_task(self.ai_processor.process_chat(chat_id)))
            
            if not tasks:
                logger.info("No chats to process")
                await asyncio.sleep(DEFAULT_MIN_DELAY)
                continue

            logger.info(f"Processing {len(tasks)} chats")
            await asyncio.gather(*tasks)
            tasks.clear()
            # Sleep if many time left
            left_time = DEFAULT_MIN_DELAY - (time.time() - last_processed)
            logger.info(f"End processing, left time: {left_time}")
            if left_time > 0:
                await asyncio.sleep(left_time)

    async def run(self):
        logger.info("Starting worker")
        update_task = asyncio.create_task(self._update_chats())
        process_task = asyncio.create_task(self._process_chats())

        await asyncio.gather(
            update_task,
            process_task,
        )

    async def _update_chats(self):
        last_processed = time.time() - DEFAULT_MAX_DELAY
        while True:
            # Get updated chats
            logger.info("Updating chats")
            chat_ids = await self.db.chat.get_updated_chats(last_processed)
            for chat_id in chat_ids:
                chat_info = self.chats.get(chat_id)
                if chat_info is None:
                    chat_info = ChatProcessInfo(chat_id=chat_id)
                    self.chats[chat_id] = chat_info
                    logger.info(f"Created chat info for chat: {chat_id}")
                chat_info.set_last_updated(time.time())
                logger.info(f"Updated chat info for chat: {chat_id}")
            logger.info(f"Updated {len(chat_ids)} chats")
            await asyncio.sleep(DEFAULT_MIN_DELAY)
            last_processed = time.time()
