from aiogram.filters.callback_data import CallbackData
from typing import Literal


class SetProviderCallbackData(CallbackData, prefix="set_provider", sep=";"):
    provider: str

class AdjustSettingCallbackData(CallbackData, prefix="settings"):
    setting: Literal[
        "messages_context_limit",
        "max_not_response_time",
        "min_delay_between_messages",
        "provider",
    ]
    action: Literal[
        "increment",
        "decrement",
        "noop",
        "toggle",
        "increment_2",
        "decrement_2",
        "open",
        "back",
    ] = "noop"
