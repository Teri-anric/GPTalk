from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.callback import SetProviderCallbackData, AdjustSettingCallbackData

PROVIDERS = {
    "openai:gpt-4o-mini": "GPT-4o Mini",
    "openai:gpt-4o": "GPT-4o",
}


def get_providers_keyboard(current_provider: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for provider, name in PROVIDERS.items():
        if provider == current_provider:
            builder.button(
                text=f"{name} ✅", callback_data=SetProviderCallbackData(provider=provider)
            )
        else:
            builder.button(
                text=name, callback_data=SetProviderCallbackData(provider=provider)
            )
    builder.add(
        InlineKeyboardButton(
            text="Back",
            callback_data=AdjustSettingCallbackData(
                setting="provider", action="back"
            ).pack(),
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def get_settings_keyboard(
    current_messages_context_limit: int,
    current_max_not_response_time: int | None,
    current_min_delay_between_messages: int | None,
    current_provider: str,
):
    """
    Create an inline keyboard for adjusting AI settings.

    :param current_context_limit: Current messages context limit
    :param current_response_time: Current max not response time in seconds
    :param current_delay_between_messages: Current min delay between messages
    """
    builder = InlineKeyboardBuilder()

    # Context Limit Buttons
    builder.row(
        InlineKeyboardButton(
            text=f"📉 Context messages count limit: {current_messages_context_limit}",
            callback_data=AdjustSettingCallbackData(
                setting="messages_context_limit", action="noop"
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="➖",
            callback_data=AdjustSettingCallbackData(
                setting="messages_context_limit", action="decrement"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="➕",
            callback_data=AdjustSettingCallbackData(
                setting="messages_context_limit", action="increment"
            ).pack(),
        ),
    )

    # Max not response time Buttons
    response_time_text = (
        f"{current_max_not_response_time / 60:2g} min"
        if current_max_not_response_time is not None
        else "Disabled"
    )
    builder.row(
        InlineKeyboardButton(
            text=f"⏱️ Max not response time: {response_time_text}",
            callback_data=AdjustSettingCallbackData(
                setting="max_not_response_time", action="toggle"
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="-1 min",
            callback_data=AdjustSettingCallbackData(
                setting="max_not_response_time", action="decrement_2"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="-30 sec",
            callback_data=AdjustSettingCallbackData(
                setting="max_not_response_time", action="decrement"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="+30 sec",
            callback_data=AdjustSettingCallbackData(
                setting="max_not_response_time", action="increment"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="+1 min",
            callback_data=AdjustSettingCallbackData(
                setting="max_not_response_time", action="increment_2"
            ).pack(),
        ),
    )

    # Min delay between messages Buttons
    delay_text = (
        f"{current_min_delay_between_messages} sec"
        if current_min_delay_between_messages is not None
        else "Disabled"
    )
    builder.row(
        InlineKeyboardButton(
            text=f"⏳ Min delay between messages: {delay_text}",
            callback_data=AdjustSettingCallbackData(
                setting="min_delay_between_messages", action="toggle"
            ).pack(),
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="-10 sec",
            callback_data=AdjustSettingCallbackData(
                setting="min_delay_between_messages", action="decrement_2"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="-5 sec",
            callback_data=AdjustSettingCallbackData(
                setting="min_delay_between_messages", action="decrement"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="+5 sec",
            callback_data=AdjustSettingCallbackData(
                setting="min_delay_between_messages", action="increment"
            ).pack(),
        ),
        InlineKeyboardButton(
            text="+10 sec",
            callback_data=AdjustSettingCallbackData(
                setting="min_delay_between_messages", action="increment_2"
            ).pack(),
        ),
    )

    model_name = PROVIDERS.get(current_provider, "Unknown")

    builder.row(
        InlineKeyboardButton(
            text=f"Model: {model_name}",
            callback_data=AdjustSettingCallbackData(
                setting="provider", action="open"
            ).pack(),
        )
    )

    return builder.as_markup()
