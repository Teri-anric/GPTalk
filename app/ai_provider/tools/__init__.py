from .base import BaseTool
from .tg import TELEGRAM_TOOLS
from .update_promt import UpdatePromt
from .scheduled import Scheduled

__all__ = ["BaseTool", "TELEGRAM_TOOLS", "UpdatePromt", "Scheduled", "get_tools"]


TOOLS: list[BaseTool] = [
    *TELEGRAM_TOOLS,
    UpdatePromt,
    Scheduled,
]


def get_tools(context: dict) -> list[BaseTool]:
    return [
        tool
        for tool in TOOLS
        if tool.filter(context)
    ]
