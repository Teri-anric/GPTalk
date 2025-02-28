from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import CallbackQuery, Message

from app.bot.callback import SetProviderCallbackData
from app.bot.keyboards import get_providers_keyboard
from app.bot.middlewares.context import DBReposContext
from app.db.models import Chat

router = Router()


@router.callback_query(SetProviderCallbackData.filter())
async def provider_callback(callback: CallbackQuery, db: DBReposContext, callback_data: SetProviderCallbackData):
    await db.chat.update_provider(callback.message.chat.id, callback_data.provider)
    await callback.message.answer("Provider updated.")



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
    
    await db.chat.update_prompt(message.chat.id, prompt)
    await message.answer(f"Prompt set to: {prompt}")


@router.message(Command("set_model"))
async def set_model_command(message: Message, db_chat: Chat):
    """
    Handle the /set-model command to set the bot's model.
    """
    current_provider = db_chat.ai_settings.provider if db_chat.ai_settings else None    
    await message.answer("Please provide a model to set.", reply_markup=get_providers_keyboard(current_provider))