from typing import Literal
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.methods import (
    BanChatMember,
    UnbanChatMember,
    RestrictChatMember,
)
from aiogram.types import ChatPermissions
from ..base import BaseTool
from .mixins import OnlyGroupChatToolMixin

FULL_PERMISSIONS = ChatPermissions(
    can_send_messages=True,
    can_send_audios=True,
    can_send_documents=True,
    can_send_photos=True,
    can_send_videos=True,
    can_send_video_notes=True,
    can_send_voice_notes=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
    can_manage_topics=True,
)
NO_PERMISSIONS = ChatPermissions(can_send_messages=False)


class ChatMemberActions(OnlyGroupChatToolMixin, BaseTool):
    """
    You can use this tool to ban, unban, mute or unmute a user in a group chat.
    until_time - util date in isoformat or action duration time in seconds (more than 366 days or less than 30 seconds or not provided - forever)
    """
    action: Literal["ban", "unban", "mute", "unmute"]
    user_id: int
    until_time: str | int | None = None

    def _parse_until_time(self) -> datetime | timedelta | None:
        if self.until_time is None:
            return None
        if isinstance(self.until_time, str):
            return datetime.fromisoformat(self.until_time)
        return datetime.now() + timedelta(seconds=self.until_time)

    async def __call__(self, bot: Bot, chat_id: int):
        actions = {
            "ban": BanChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                until_date=self._parse_until_time(),
            ),
            "unban": UnbanChatMember(chat_id=chat_id, user_id=self.user_id),
            "mute": RestrictChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                permissions=NO_PERMISSIONS,
                until_date=self._parse_until_time(),
            ),
            "unmute": RestrictChatMember(
                chat_id=chat_id,
                user_id=self.user_id,
                permissions=FULL_PERMISSIONS,
                until_date=self._parse_until_time(),
            ),
        }
        await bot(actions[self.action])
