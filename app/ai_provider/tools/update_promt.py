from .base import BaseTool

from app.db.context import DBReposContext


class UpdatePromt(BaseTool):
    """
    Update user instructions in current chat.
    You can use this tool to memorize and other.
    """
    new_instructions: str

    async def __call__(self, db: DBReposContext, chat_id: int):
        await db.chat.update_ai_settings(chat_id, prompt=self.new_instructions)
        return "User instructions updated"