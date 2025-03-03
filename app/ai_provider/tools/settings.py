from .base import BaseTool

from app.db.context import DBReposContext


class UpdateSettings(BaseTool):
    """
    Update settings for current chat.
    You can use this tool to update user instructions, messages context limit, max not response time and min delay between messages.
    not provided fields will not be updated.
    """
    instructions: str | None = None
    messages_context_limit: int | None = None
    min_delay_between_messages: int | None = None
    max_not_response_time: int | None = None

    async def __call__(self, db: DBReposContext, chat_id: int):
        data = {}
        if self.instructions is not None:
            data["prompt"] = self.instructions
        if self.messages_context_limit is not None:
            data["messages_context_limit"] = self.messages_context_limit
        if self.min_delay_between_messages is not None:
            data["min_delay_between_messages"] = self.min_delay_between_messages
        if self.max_not_response_time is not None:
            data["max_not_response_time"] = self.max_not_response_time
        settings = await db.chat.update_ai_settings(
            chat_id,
            **data
        )
        return {
            "instructions": settings.prompt,
            "messages_context_limit": settings.messages_context_limit,
            "min_delay_between_messages": settings.min_delay_between_messages,
            "max_not_response_time": settings.max_not_response_time,
        }
