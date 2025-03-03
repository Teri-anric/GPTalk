import asyncio
import logging

from app.db import DBReposContext, MessageType

MINIMAL_SLEEP = 10

logger = logging.getLogger(__name__)

class ScheduledWorker:
    def __init__(self, assistant_id: int):
        self.db = DBReposContext()
        self.assistant_id = assistant_id
    
    async def _run(self):
        logger.info("Running scheduled worker")
        scheduled_messages = await self.db.scheduled.get_all_not_done()
        for scheduled_message in scheduled_messages:
            await self.db.message.create_message(
                chat_id=scheduled_message.chat_id,
                from_user_id=self.assistant_id,
                type=MessageType.NOTIFICATION,
                content=scheduled_message.message,
            )
        await self.db.scheduled.marks_as_done([s.id for s in scheduled_messages])
        logger.info(f"Scheduled worker finished. Processed {len(scheduled_messages)} messages")

    async def run(self):
        while True:
            await self._run()
            await asyncio.sleep(MINIMAL_SLEEP)
