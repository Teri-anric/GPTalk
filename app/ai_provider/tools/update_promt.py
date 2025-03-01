from .base import BaseTool

from app.db.context import DBReposContext


class UpdatePromt(BaseTool):
    """
    Update user instructions in current chat.
    You can use this tool to memorize and other.
    """
    new_instructions: str

    async def __call__(self, db: DBReposContext, chat_id: int):
        await db.chat.update_prompt(chat_id, self.new_instructions)
        return "user instructions updated"