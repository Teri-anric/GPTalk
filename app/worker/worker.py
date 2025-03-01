import time
import asyncio
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from .logger import logger

from aiogram import Bot

from app.ai_provider import AIProvider
from app.worker.ai_processor import AIProcessor
from app.db import DBReposContext

MINIMAL_SLEEP = 1  # 1 seconds


@dataclass
class ChatProcessInfo:
    chat_id: int
    last_processed: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    max_not_response_time: float | None = None
    min_delay_between_messages: float | None = None

    def is_ready_to_process(self) -> bool:
        is_ready = False    
        time_diff = time.time() - self.last_processed
        # Check max delay
        if self.max_not_response_time is not None:
            is_ready = time_diff > self.max_not_response_time
        # Check last updated
        if self.last_updated >= self.last_processed:
            is_ready = True
        # Check min delay
        if is_ready and self.min_delay_between_messages is not None:
            is_ready = time_diff > self.min_delay_between_messages
        # Update last processed
        if is_ready:
            self.last_processed = time.time()
        return is_ready

    def set_last_updated(self, last_updated: float):
        self.last_updated = last_updated


class BackgroundChatsProcessor:
    """
    Background task for processing chats.
    """

    def __init__(self, bot: Bot, **workflow_data):
        self.bot = bot
        self.ai_provider = AIProvider()
        self.workflow_data = workflow_data

        self.chats: dict[int, ChatProcessInfo] = {}

    async def _process_chats(self):
        tasks = []
        ai_processor = AIProcessor(
            self.bot,
            self.ai_provider,
            **self.workflow_data,
        )
        while True:
            last_processed = time.time()
            logger.debug(f"Start processing {len(self.chats)} chats")
            for chat_id in list(self.chats.keys()):
                chat_info = self.chats[chat_id]
                if not chat_info.is_ready_to_process():
                    logger.debug(f"Chat {chat_id} is not ready to process")
                    continue
                logger.info(f"Adding chat to process: {chat_id}")
                tasks.append(
                    asyncio.create_task(ai_processor.process_chat(chat_id))
                )

            if not tasks:
                logger.debug("No chats to process")
                await asyncio.sleep(MINIMAL_SLEEP)
                continue

            logger.info(f"Processing {len(tasks)} chats")
            await asyncio.gather(*tasks)
            tasks.clear()
            # Sleep if many time left
            left_time = MINIMAL_SLEEP - (time.time() - last_processed)
            logger.info(f"End processing, left time: {left_time}")
            if left_time > 0:
                await asyncio.sleep(left_time)

    async def run(self):
        logger.info("Starting worker")
        await asyncio.gather(
            self._update_chats(),
            self._process_chats(),
        )

    async def _update_chats(self):
        last_processed = datetime.fromtimestamp(0.0)
        db = DBReposContext()
        while True:
            # Get updated chats
            chat_ids = await db.chat.get_updated_chats(last_processed)
            for chat_id in chat_ids:
                chat_info = self.chats.get(chat_id)
                if chat_info is None:
                    chat_info = ChatProcessInfo(chat_id=chat_id)
                    self.chats[chat_id] = chat_info
                    logger.info(f"Created chat info for chat: {chat_id}")
                chat_info.set_last_updated(time.time())
                logger.info(f"Updated chat info for chat: {chat_id}")
            last_processed = datetime.now()
            await asyncio.sleep(MINIMAL_SLEEP)

