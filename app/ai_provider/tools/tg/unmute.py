from ..base import BaseTool

from aiogram import Bot
from aiogram.methods import RestrictChatMember
from aiogram.types import ChatPermissions

class Unmute(BaseTool):
    user_id: int

    async def __call__(self, bot: Bot, chat_id: int):
        return await bot(
            RestrictChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_send_polls=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                    can_manage_topics=True
                ),
            )
        )
