import logging
from datetime import datetime

from aiogram import Bot

from app.db import DBReposContext
from app.db import MessageType
from app.db import Chat

from app.ai_provider import AIProvider
from app.ai_provider.tools import BaseTool, get_tools
from app.ai_provider.services.base import AiResponse
from app.ai_provider.conversation import ConversationBuilder

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self, bot: Bot, ai_provider: AIProvider, **workflow_data):
        self.db = DBReposContext()
        self.bot = bot
        self.ai_provider = ai_provider
        self.conversation_builder = ConversationBuilder(self.assistant_user_id)
        self.workflow_data = workflow_data
    
    async def _get_chat(self, chat_id: int) -> Chat:
        db_chat = await self.db.chat.get_chat_by_id(chat_id=chat_id)
        if db_chat is None:
            raise ValueError(f"Chat {chat_id} not found")
        return db_chat

    @property
    def assistant_user_id(self) -> int:
        return self.bot.id

    def _get_context(self, chat: Chat) -> dict:
        return {
            "bot": self.bot,
            "chat": chat,
            "chat_id": chat.id,
            "db": self.db,
            "assistant_id": self.assistant_user_id,
            **self.workflow_data,
        }

    async def process_chat(
        self,
        chat_id: int,
        last_seen_date: datetime,
    ):
        chat = await self._get_chat(chat_id)
        await self.bot.send_chat_action(chat.id, action="typing")
        response = await self._generate_response(chat=chat, last_seen_date=last_seen_date)
        await self._process_ai_response(chat=chat, response=response)


    async def _process_tool_call(
        self,
        tools: list[BaseTool],
        chat: Chat,
    ):
        logger.debug(f"Processing tool calls for chat_id: {chat.id}")
        if not tools:
            logger.debug(f"No tools provided for processing for chat_id: {chat.id}")
            return

        tools_results = {}
        for tool in tools:
            try:
                logger.debug(f"Running tool: {tool.extra_payload}")
                result_tool = await tool.run(
                    context=self._get_context(chat)
                )
            except Exception as e:
                logger.error(f"Error running tool {tool.extra_payload.get('id')}: {str(e)}")
                result_tool = str(e)

            tools_results[tool.extra_payload.get("id")] = result_tool

        await self.db.message.create_message(
            chat_id=chat.id,
            from_user_id=self.assistant_user_id,
            type=MessageType.TOOL_CALLS,
            payload=dict(
                tool_calls=[tool.extra_payload for tool in tools],
                tool_calls_results=tools_results,
            ),
        )
        logger.info(f"Tool calls processed for chat_id: {chat.id}")

    async def _generate_response(
        self,
        chat: Chat,
        last_seen_date: datetime,
    ):
        logger.debug(f"Generating response for chat_id: {chat.id}")
        # Get ai service
        ai_service = self.ai_provider.get_ai_service(chat.ai_settings.provider)
        if ai_service is None:
            logger.error(f"AI service {chat.ai_settings.provider} not found")
            raise ValueError(f"AI service {chat.ai_settings.provider} not found")
        # Get last messages from db
        messages = await self.db.message.get_last_messages(
            chat_id=chat.id,
            limit=chat.ai_settings.messages_context_limit,
        )
        # Prepare messages for ai
        conversation = self.conversation_builder.build(
            chat=chat,
            messages=reversed(messages),
            last_seen_date=last_seen_date,
        )
        logger.debug(f"Conversation by {chat.id}: {conversation}")
        # Generate response from ai
        response = await ai_service.generate_response(
            messages=conversation, tools=get_tools(context=self._get_context(chat))
        )
        logger.debug(f"Response generated for chat_id: {chat.id}")
        return response

    async def _process_ai_response(
        self,
        chat: Chat,
        response: AiResponse,
    ):
        logger.debug(f"Processing AI response for chat_id: {chat.id}")
        # Save response to db
        if response.response:
            await self.db.message.create_message(
                chat_id=chat.id,
                from_user_id=self.assistant_user_id,
                type=MessageType.AI_REFLECTION,
                content=response.response,
            )
            logger.info(f"AI response saved for chat_id: {chat.id}")
        # Process tool call
        await self._process_tool_call(
            tools=response.tools,
            chat=chat,
        )
