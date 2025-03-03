import json

from aiogram import Bot, Router, flags
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import BufferedInputFile

from app.db import DBReposContext
from app.db import Chat

from app.ai_provider.conversation import ConversationBuilder

router = Router()


@router.message(Command("export"))
@flags.not_saved
async def export_command(message: Message, db: DBReposContext, bot: Bot, db_chat: Chat):
    conversation_builder = ConversationBuilder(assistant_user_id=bot.id)
    messages = await db.message.get_last_messages(
        chat_id=db_chat.id,
        limit=db_chat.ai_settings.messages_context_limit,
    )
    conversation = conversation_builder.build(
        chat=db_chat, messages=reversed(messages)
    )
    await bot.send_document(
        message.chat.id,
        BufferedInputFile(
            json.dumps(conversation, indent=2, ensure_ascii=False).encode("utf-8"),
            filename="conversation.json",
        ),
        caption="Conversation export",
    )
