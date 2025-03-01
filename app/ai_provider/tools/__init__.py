from .base import BaseTool
from .tg import TELEGRAM_TOOLS
from .update_promt import UpdatePromt
from .self_notify import SelfNotify

__all__ = ["BaseTool", "TELEGRAM_TOOLS", "UpdatePromt", "SelfNotify"]


TOOLS = [
    *TELEGRAM_TOOLS,
    UpdatePromt,
    SelfNotify,
]
