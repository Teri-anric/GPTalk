"""
Handlers for incoming messages from users.
"""

from datetime import datetime

from aiogram import F, Router, Bot
from aiogram.types import Message as TelegramMessage

from app.bot.middlewares.context import DBReposContext
from app.db.models.chat import Chat
from app.db.models.messages import Message, MessageType
from app.db.models.user import User

from ..ai_provider import AIProvider
from ..ai_provider.tools import BaseTool, AnswerTool

router = Router()


async def _prepare_messages(prompt: str, messages: list[Message]) -> list[dict]:
    conversation = [{"role": "system", "content": prompt}]
    for message in messages:
        if message.type == MessageType.TOOL_CALL:
            conversation.extend(
                [
                    {
                        "role": "tool",
                        "content": message.payload["result"],
                        "tool_call_id": message.payload["tool_call_id"],
                    },
                ]
            )
            continue
        # default to show content of the message
        if message.content is None:
            continue
        conversation.append({"role": "user", "content": message.content})
    return conversation


async def _process_tool_call(
    tools: list[BaseTool], db: DBReposContext, db_chat: Chat, db_user: User, bot: Bot
):
    for tool in tools:
        try:
            result_tool = await tool.run(
                context={"bot": bot, "chat_id": db_chat.id, "user_id": db_user.id}
            )
        except Exception as e:
            result_tool = str(e)

        await db.message.create_message(
            chat_id=db_chat.id,
            from_user_id=bot.id,
            type=MessageType.TOOL_CALL,
            content="",
            payload={"tool_call_id": tool.tool_call_id, "result": result_tool},
            send_at=datetime.now()
        )


@router.message(F.text)
async def message_handler(
    message: TelegramMessage,
    db_user: User,
    db_chat: Chat,
    db: DBReposContext,
    ai_provider: AIProvider,
    bot: Bot,
):
    """
    Process an incoming message from a user.

    Args:
        message (Message): The incoming Telegram message.
    """
    await message.answer("Processing...")

    if db_chat.ai_settings is None:
        return  # bot is not configured to answer in this chat

    ai_service = ai_provider.get_ai_service(db_chat.ai_settings.provider)
    if ai_service is None:
        return  # ai service not found

    messages = await db.message.get_last_messages(
        chat_id=db_chat.id, limit=db_chat.ai_settings.messages_limit
    )

    response = await ai_service.generate_response(
        messages=await _prepare_messages(
            prompt=db_chat.ai_settings.prompt, messages=messages
        ),
        tools=[AnswerTool],
    )

    await _process_tool_call(
        tools=response.tools, db=db, db_chat=db_chat, db_user=db_user, bot=bot
    )
