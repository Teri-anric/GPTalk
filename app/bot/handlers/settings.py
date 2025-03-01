from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, Message

from app.bot.callback import SetProviderCallbackData, AdjustSettingCallbackData
from app.bot.keyboards import get_providers_keyboard, get_settings_keyboard
from app.db import DBReposContext
from app.db import Chat

router = Router()


@router.message(Command("set_prompt"))
async def set_command(message: Message, command: CommandObject, db: DBReposContext):
    """
    Handle the /set-prompt command to set the bot's prompt.

    Args:
        message (Message): The incoming Telegram message with the /set-prompt command.
    """
    prompt = command.args
    if not prompt and message.reply_to_message is not None:
        prompt = message.reply_to_message.text

    if prompt is None:
        await message.answer("Please provide a prompt to set.")
        return

    await db.chat.update_ai_settings(message.chat.id, prompt=prompt)
    await message.answer(f"Prompt set to: {prompt}")


@router.message(Command("settings"))
async def settings_command(message: Message, db_chat: Chat):
    """
    Show settings adjustment menu.
    """
    current_limit = 10
    current_response_time = None
    current_delay_between_messages = None
    current_provider = None
    if db_chat.ai_settings:
        current_limit = db_chat.ai_settings.messages_context_limit
        current_response_time = db_chat.ai_settings.max_not_response_time
        current_delay_between_messages = db_chat.ai_settings.min_delay_between_messages
        current_provider = db_chat.ai_settings.provider

    await message.answer(
        "🔧 AI Settings Adjustment Menu",
        reply_markup=get_settings_keyboard(
            current_limit,
            current_response_time,
            current_delay_between_messages,
            current_provider,
        ),
    )


@router.callback_query(
    AdjustSettingCallbackData.filter((F.setting == "provider") & (F.action == "open"))
)
async def provider_open_callback(callback: CallbackQuery, db_chat: Chat):
    """
    Handle the /set-model command to set the bot's model.
    """
    current_provider = db_chat.ai_settings.provider if db_chat.ai_settings else None
    await callback.message.edit_text(
        "Please select a provider.",
        reply_markup=get_providers_keyboard(current_provider),
    )
    await callback.answer()


@router.callback_query(SetProviderCallbackData.filter())
async def provider_callback(
    callback: CallbackQuery, callback_data: SetProviderCallbackData, db: DBReposContext
):
    await db.chat.update_ai_settings(
        callback.message.chat.id, provider=callback_data.provider
    )
    await callback.message.edit_reply_markup(
        reply_markup=get_providers_keyboard(callback_data.provider),
    )
    await callback.answer("Provider updated.")


@router.callback_query(
    AdjustSettingCallbackData.filter(F.setting == "provider" & F.action == "back")
)
async def provider_back_callback(
    callback: CallbackQuery, db_chat: Chat, callback_data: AdjustSettingCallbackData
):
    """
    Show settings adjustment menu.
    """
    current_limit = 10
    current_response_time = None
    current_delay_between_messages = None
    current_provider = None
    if db_chat.ai_settings:
        current_limit = db_chat.ai_settings.messages_context_limit
        current_response_time = db_chat.ai_settings.max_not_response_time
        current_delay_between_messages = db_chat.ai_settings.min_delay_between_messages
        current_provider = db_chat.ai_settings.provider

    await callback.message.edit_text(
        "🔧 AI Settings Adjustment Menu",
        reply_markup=get_settings_keyboard(
            current_limit,
            current_response_time,
            current_delay_between_messages,
            current_provider,
        ),
    )


@router.callback_query(AdjustSettingCallbackData.filter())
async def adjust_setting_callback(
    callback: CallbackQuery,
    callback_data: AdjustSettingCallbackData,
    db: DBReposContext,
    db_chat: Chat,
):
    """
    Handle settings adjustment via inline keyboard.
    """
    if callback_data.action == "noop":
        await callback.answer("No action required.")
        return
    actions = {
        "messages_context_limit": {
            "increment": lambda x: x + 1,
            "decrement": lambda x: x - 1,
            "increment_2": lambda x: x + 2,
            "decrement_2": lambda x: x - 2,
        },
        "max_not_response_time": {
            "increment": lambda x: x + 30,
            "decrement": lambda x: x - 30,
            "increment_2": lambda x: x + 60,
            "decrement_2": lambda x: x - 60,
            "toggle": lambda x: 60 * 60 if x is None else None,
        },
        "min_delay_between_messages": {
            "increment": lambda x: x + 5,
            "decrement": lambda x: x - 5,
            "increment_2": lambda x: x + 10,
            "decrement_2": lambda x: x - 10,
            "toggle": lambda x: 10 if x is None else None,
        },
    }
    data = {
        "messages_context_limit": db_chat.ai_settings.messages_context_limit,
        "max_not_response_time": db_chat.ai_settings.max_not_response_time,
        "min_delay_between_messages": db_chat.ai_settings.min_delay_between_messages,
        "provider": db_chat.ai_settings.provider,
    }
    # modify data
    action = actions[callback_data.setting][callback_data.action]
    if not action:
        await callback.answer("Invalid action.")
        return
    data[callback_data.setting] = action(data[callback_data.setting])
    if data[callback_data.setting] is not None and data[callback_data.setting] < 0:
        return callback.answer("Value cannot be negative.")
    # update db
    await db.chat.update_ai_settings(
        callback.message.chat.id,
        **{
            callback_data.setting: data[callback_data.setting],
        },
    )
    # update keyboard

    await callback.message.edit_reply_markup(
        reply_markup=get_settings_keyboard(
            current_messages_context_limit=data["messages_context_limit"],
            current_max_not_response_time=data["max_not_response_time"],
            current_min_delay_between_messages=data["min_delay_between_messages"],
            current_provider=data["provider"],
        )
    )
    await callback.answer("Settings updated.")

