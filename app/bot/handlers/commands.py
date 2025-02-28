"""
Handlers for commands from users.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.types import Message

from app.db import DBReposContext

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
