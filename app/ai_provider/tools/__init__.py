from .base import BaseTool
from .tg import TELEGRAM_TOOLS
from .settings import UpdateSettings
from .scheduled import Scheduled

__all__ = ["BaseTool", "TELEGRAM_TOOLS", "UpdateSettings", "Scheduled", "get_tools"]


TOOLS: list[BaseTool] = [
    *TELEGRAM_TOOLS,
    UpdateSettings,
    Scheduled,
]


def get_tools(context: dict) -> list[BaseTool]:
    return [
        tool
        for tool in TOOLS
        if tool.filter(context)
    ]
