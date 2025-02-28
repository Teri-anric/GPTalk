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
from app.constants import BASE_PROMPT, TEXT_MESSAGE_IN_CHAT

router = Router()

async def _prepare_tool_call_message(message: Message) -> list[dict]:
    tool_calls = message.payload["tool_calls"]
    tool_calls_results = message.payload["tool_calls_results"]

    conversation = [
        {
            "role": "assistant",
            "tool_calls": tool_calls,
        }
    ]
    for tool_call in tool_calls:
        tool_call_result = tool_calls_results[tool_call["id"]] or "**Tool call not completed**"
        conversation.append(
            {
                "role": "tool",
                "content": tool_call_result,
                "tool_call_id": tool_call["id"],
            }
        )
    return conversation

async def _prepare_message_text(message: Message, assistant_user_id: int) -> list[dict]:
    if not message.content:
        return []

    role = "user"
    if message.from_user_id == assistant_user_id:
        role = "assistant"

    return [
        {
            "role": role,
            "content": TEXT_MESSAGE_IN_CHAT.format(
                message_id=message.telegram_id,
                from_user_id=message.from_user_id,
                user_message=message.content,
            ),
        }
    ]

async def _prepare_messages(
    prompt: str, messages: list[Message], assistant_user_id: int
) -> list[dict]:
    conversation = [
        {
            "role": "system",
            "content": BASE_PROMPT.format(
                user_instructions=prompt,
            ),
        }
    ]
    for message in messages:    
        if message.type == MessageType.TOOL_CALLS:
            conversation.extend(await _prepare_tool_call_message(message))
            continue

        if message.type in (MessageType.AI_REFLECTION, MessageType.TEXT):
            conversation.extend(await _prepare_message_text(message, assistant_user_id))
            continue

    return conversation


async def _process_tool_call(
    tools: list[BaseTool],
    chat_id: int,
    db: DBReposContext,
    bot: Bot,
):
    if not tools:
        return

    tools_results = {}
    for tool in tools:
        try:
            result_tool = await tool.run(
                context={
                    "bot": bot,
                    "chat_id": chat_id,
                }
            )
        except Exception as e:
            result_tool = str(e)

        tools_results[tool.extra_payload.get("id")] = result_tool

    await db.message.create_message(
        chat_id=chat_id,
        from_user_id=bot.id,
        type=MessageType.TOOL_CALLS,
        payload=dict(
            tool_calls=[tool.extra_payload for tool in tools],
            tool_calls_results=tools_results,
        ),
    )


async def process_chat(
    db_chat: Chat,
    db: DBReposContext,
    ai_provider: AIProvider,
    bot: Bot,
):
    ai_service = ai_provider.get_ai_service(db_chat.ai_settings.provider)
    if ai_service is None:
        return  # ai service not found

    messages = await db.message.get_last_messages(
        chat_id=db_chat.id,
        limit=db_chat.ai_settings.messages_limit,
    )
    conversation = await _prepare_messages(
        prompt=db_chat.ai_settings.prompt,
        messages=reversed(messages),
        assistant_user_id=bot.id,
    )

    response = await ai_service.generate_response(
        messages=conversation, tools=[AnswerTool]
    )
    if response.response:
        await db.message.create_message(
            chat_id=db_chat.id,
            from_user_id=bot.id,
            type=MessageType.AI_REFLECTION,
            content=response.response,
        )
    await _process_tool_call(
        tools=response.tools,
        db=db,
        db_chat=db_chat,
        bot=bot,
    )


@router.message(F.text)
async def message_handler(
    _: TelegramMessage,
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
    if db_chat.ai_settings is None:
        return  # bot is not configured to answer in this chat

    await process_chat(
        db_chat=db_chat,
        db=db,
        ai_provider=ai_provider,
        bot=bot,
    )
