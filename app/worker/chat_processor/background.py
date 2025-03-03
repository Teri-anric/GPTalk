import logging
import time
import asyncio
from datetime import datetime

from aiogram import Bot

from app.ai_provider import AIProvider
from app.db import DBReposContext, MessageType

from .ai_processor import AIProcessor
from .types import ChatProcessInfo


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MINIMAL_SLEEP = 1  # 1 seconds


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
                tasks.append(asyncio.create_task(ai_processor.process_chat(chat_id)))

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

    def _set_default_chat_info(self, chat_id: int) -> ChatProcessInfo:
        chat_info = self.chats.get(chat_id)
        if chat_info is None:
            chat_info = ChatProcessInfo(chat_id=chat_id)
            self.chats[chat_id] = chat_info
            logger.info(f"Created chat info for chat: {chat_id}")
        return chat_info

    async def _update_chats(self):
        last_processed = datetime.fromtimestamp(0.0)
        db = DBReposContext()
        while True:
            # Get updated chats settings
            chats_settings = await db.chat.get_updated_chats_settings(last_processed)
            for chat_setting in chats_settings:
                chat_info = self._set_default_chat_info(chat_setting.chat_id)
                chat_info.update_settings(chat_setting)
                chat_info.set_last_updated(last_processed.timestamp())
                logger.info(f"Updated chat info for chat: {chat_setting.chat_id}")
            # Update last processed
            chat_ids = await db.chat.get_awaible_new_messages_in_chats(
                last_processed,
                except_types=[MessageType.TOOL_CALLS],  # MessageType.AI_REFLECTION
            )
            for chat_id in chat_ids:
                chat_info = self._set_default_chat_info(chat_id)
                chat_info.set_last_updated(last_processed.timestamp())
                logger.info(f"Updated chat info for chat: {chat_id}")
            last_processed = datetime.now()
            await asyncio.sleep(MINIMAL_SLEEP)
