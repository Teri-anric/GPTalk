from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback import SetProviderCallbackData

PROVIDERS = {
    "openai:gpt-4o-mini": "GPT-4o Mini",
    "openai:gpt-4o": "GPT-4o",
}


def get_providers_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for provider, name in PROVIDERS.items():
        builder.button(text=name, callback_data=SetProviderCallbackData(provider=provider))
    return builder.as_markup()
