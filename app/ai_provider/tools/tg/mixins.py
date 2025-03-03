from app.db import ChatType

from app.ai_provider.tools.base import BaseTool

class OnlyGroupChatToolMixin(BaseTool):
    @classmethod
    def filter(cls, context: dict) -> bool:
        return context["chat"].type in [ChatType.GROUP, ChatType.SUPERGROUP]

class OnlyPrivateChatToolMixin(BaseTool):
    @classmethod
    def filter(cls, context: dict) -> bool:
        return context["chat"].type == ChatType.PRIVATE

class OnlyChannelChatToolMixin(BaseTool):
    @classmethod
    def filter(cls, context: dict) -> bool:
        return context["chat"].type == ChatType.CHANNEL
