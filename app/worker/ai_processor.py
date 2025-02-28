import logging

from aiogram import Bot

from app.db import DBReposContext
from app.db import Message, MessageType
from app.db import ChatAISettings

from app.ai_provider import AIProvider
from app.ai_provider.tools import BaseTool, AnswerTool
from app.ai_provider.services.base import AiResponse

from app.constants import BASE_PROMPT, TEXT_MESSAGE_IN_CHAT, NOT_RESPONSE_TOOL_MESSAGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProcessor:
    def __init__(self, db: DBReposContext, bot: Bot, ai_provider: AIProvider, **workflow_data):
        self.db = db
        self.bot = bot
        self.ai_provider = ai_provider
        self.workflow_data = workflow_data
    
    async def _get_chat_settings(self, chat_id: int) -> ChatAISettings:
        db_chat = await self.db.chat.get_chat_by_id(chat_id=chat_id)
        if db_chat is None:
            raise ValueError(f"Chat {chat_id} not found")
        return db_chat.ai_settings

    @property
    def assistant_user_id(self) -> int:
        return self.bot.id

    def _prepare_tool_call_message(self, message: Message) -> list[dict]:
        tool_calls = message.payload["tool_calls"]
        tool_calls_results = message.payload["tool_calls_results"]

        conversation = [
            {
                "role": "assistant",
                "tool_calls": tool_calls,
            }
        ]
        for tool_call in tool_calls:
            tool_call_result = tool_calls_results[tool_call["id"]] or NOT_RESPONSE_TOOL_MESSAGE
            conversation.append(
                {
                    "role": "tool",
                    "content": tool_call_result,
                    "tool_call_id": tool_call["id"],
                }
            )
        return conversation


    def _prepare_message_text(self, message: Message) -> list[dict]:
        if not message.content:
            return []
        role = "user"
        if message.from_user_id == self.assistant_user_id:
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

    def _prepare_messages(
        self,
        prompt: str,
        messages: list[Message]
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
                conversation.extend(self._prepare_tool_call_message(message))
            if message.type in (MessageType.AI_REFLECTION, MessageType.TEXT):
                conversation.extend(self._prepare_message_text(message))
        return conversation


    async def _process_tool_call(
        self,
        tools: list[BaseTool],
        chat_id: int
    ):
        logger.debug(f"Processing tool calls for chat_id: {chat_id}")
        if not tools:
            logger.debug(f"No tools provided for processing for chat_id: {chat_id}")
            return

        tools_results = {}
        for tool in tools:
            try:
                logger.debug(f"Running tool: {tool.extra_payload}")
                result_tool = await tool.run(
                    context={
                        "bot": self.bot,
                        "chat_id": chat_id,
                        "db": self.db,
                        **self.workflow_data,
                    }
                )
            except Exception as e:
                logger.error(f"Error running tool {tool.extra_payload.get('id')}: {str(e)}")
                result_tool = str(e)

            tools_results[tool.extra_payload.get("id")] = result_tool

        await self.db.message.create_message(
            chat_id=chat_id,
            from_user_id=self.assistant_user_id,
            type=MessageType.TOOL_CALLS,
            payload=dict(
                tool_calls=[tool.extra_payload for tool in tools],
                tool_calls_results=tools_results,
            ),
        )
        logger.info(f"Tool calls processed for chat_id: {chat_id}")

    async def _generate_response(
        self,
        chat_id: int,
        chat_settings: ChatAISettings,
    ):
        logger.debug(f"Generating response for chat_id: {chat_id}")
        # Get ai service
        ai_service = self.ai_provider.get_ai_service(chat_settings.provider)
        if ai_service is None:
            logger.error(f"AI service {chat_settings.provider} not found")
            raise ValueError(f"AI service {chat_settings.provider} not found")
        # Get last messages from db
        messages = await self.db.message.get_last_messages(
            chat_id=chat_id,
            limit=chat_settings.messages_limit,
        )
        # Prepare messages for ai
        conversation = self._prepare_messages(
            prompt=chat_settings.prompt,
            messages=reversed(messages),
        )
        logger.debug(f"Conversation by {chat_id}: {conversation}")
        # Generate response from ai
        response = await ai_service.generate_response(
            messages=conversation, tools=[AnswerTool]
        )
        logger.debug(f"Response generated for chat_id: {chat_id}")
        return response

    async def _process_ai_response(
        self,
        chat_id: int,
        response: AiResponse,
    ):
        logger.debug(f"Processing AI response for chat_id: {chat_id}")
        # Save response to db
        if response.response:
            await self.db.message.create_message(
                chat_id=chat_id,
                from_user_id=self.assistant_user_id,
                type=MessageType.AI_REFLECTION,
                content=response.response,
            )
            logger.info(f"AI response saved for chat_id: {chat_id}")
        # Process tool call
        await self._process_tool_call(
            tools=response.tools,
            chat_id=chat_id,
        )

    async def process_chat(
        self,
        chat_id: int,
    ):
        chat_settings = await self._get_chat_settings(chat_id)
        response = await self._generate_response(
            chat_id=chat_id,
            chat_settings=chat_settings,
        )
        await self._process_ai_response(
            chat_id=chat_id,
            response=response,
        )
