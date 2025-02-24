"""
Handlers for commands from users.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from app.bot.middlewares.context import DBReposContext

router = Router()


@router.message(Command("start"))
async def start_command(message: Message):
    """
    Handle the /start command for new users.

    Args:
        message (Message): The incoming Telegram message with the /start command.
    """
    await message.answer(
        "🚀 Welcome to TelegramThreadAI!\n\n"
        "I'll help you manage AI-enhanced group conversations. "
        "Create or join chats to start interacting!"
    )


@router.message(Command("help"))
async def help_command(message: Message):
    """
    Handle the /help command to provide user guidance.

    Args:
        message (Message): The incoming Telegram message with the /help command.
    """
    await message.answer(
        """
    /start - Start the bot
    """
    )


@router.message(Command("set-prompt"))
async def set_command(message: Message, command: CommandObject, db: DBReposContext):
    """
    Handle the /set-prompt command to set the bot's prompt.

    Args:
        message (Message): The incoming Telegram message with the /set command.
    """
    prompt = command.args
    if not prompt and message.reply_to_message is not None:
        prompt = message.reply_to_message.text
    
    if prompt is None:
        await message.answer("Please provide a prompt to set.")
        return
    
    await db.chat.update_prompt(message.chat.id, prompt)
    await message.answer(f"Prompt set to: {prompt}")


@router.message(Command("set-model"))
async def set_model_command(message: Message, command: CommandObject):
    """
    Handle the /set-model command to set the bot's model.
    """
    await message.answer("Model set to: gpt-4o-mini")