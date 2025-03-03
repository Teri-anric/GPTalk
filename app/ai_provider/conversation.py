import json
from app.constants import (
    BASE_PROMPT,
    TEXT_MESSAGE_IN_CHAT,
    NOT_RESPONSE_TOOL_MESSAGE,
    USER_IN_CHAT,
    REPLY_TO_MESSAGE_IN_CHAT,
    NOTIFICATION_MESSAGE_IN_CHAT,
    SHORT_USER_IN_CHAT,
    EXTERNAL_REPLY_IN_CHAT,
)
from app.db import Message, MessageType, User, Chat
from datetime import datetime


class ConversationBuilder:
    def __init__(self, assistant_user_id: int):
        self.assistant_user_id = assistant_user_id

    def build(self, chat: Chat, messages: list[Message]):
        return self._prepare_messages(chat, messages)

    def _prepare_messages(self, chat: Chat, messages: list[Message]) -> list[dict]:
        conversation = [
            {
                "role": "system",
                "content": BASE_PROMPT.format(
                    user_instructions=chat.ai_settings.prompt,
                    current_time=datetime.now().isoformat(),
                    chat_id=chat.id,
                    chat_type=chat.type,
                    chat_title=chat.title,
                    chat_username=chat.username
                ),
            }
        ]
        for message in messages:
            if message.type == MessageType.TOOL_CALLS:
                conversation.extend(self._prepare_tool_call_message(message))
            if message.type in (MessageType.AI_REFLECTION, MessageType.TEXT):
                conversation.extend(self._prepare_message_text(message, messages))
            if message.type == MessageType.NOTIFICATION:
                conversation.extend(
                    self._prepare_notification_message(message, messages)
                )
        return conversation

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
            tool_call_result = (
                tool_calls_results[tool_call["id"]] or NOT_RESPONSE_TOOL_MESSAGE
            )
            conversation.append(
                {
                    "role": "tool",
                    "content": json.dumps(tool_call_result),
                    "tool_call_id": tool_call["id"],
                }
            )
        return conversation
    
    def _get_user_info(self, user: User | None) -> dict:
        user_info = {
            "username": "",
            "first_name": "",
            "last_name": "",
        }
        if user:
            user_info = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
        return user_info


    def _get_reply_to_user(self, message: Message, messages: list[Message]) -> str:
        reply_to = message.payload.get("reply_to")
        if reply_to is None:
            return ""
        reply_to_user = SHORT_USER_IN_CHAT.format(
            tag="reply_to_user",
            user_id=reply_to.get("user_id"),
        )
        user = next(
            (m.from_user for m in messages if m.from_user_id == reply_to.get("user_id")), None
        )
        if user is not None:
            reply_to_user = USER_IN_CHAT.format(
                tag="reply_to_user",
                user_id=reply_to.get("user_id"),
                **self._get_user_info(user),
            )
        return reply_to_user
    
    def _get_reply_to_message(self, message: Message, messages: list[Message]) -> str:
        reply_to = (message.payload or {}).get("reply_to")
        if reply_to is None:
            return ""
        
        reply_type_content = "text"
        reply_to_content = reply_to.get("content")
        if len(reply_to_content) > 50:
            reply_type_content = "short-text"
            reply_to_content = reply_to_content[:50] + "..."
        if reply_to.get("type") == "quote":
            reply_type_content = "quote"
                
        reply_to_user = self._get_reply_to_user(message, messages)
        if reply_to.get("type") == "external":
            return EXTERNAL_REPLY_IN_CHAT.format(
                reply_to_id=reply_to.get("id"),
                reply_to_user=reply_to_user,
                reply_to_content=reply_to_content,
                reply_type_content=reply_type_content
            )
        return REPLY_TO_MESSAGE_IN_CHAT.format(
            reply_to_id=reply_to.get("id"),
            reply_to_user=reply_to_user,
            reply_to_content=reply_to_content,
            reply_type_content=reply_type_content
        )

    def _prepare_message_text(
        self, message: Message, messages: list[Message]
    ) -> list[dict]:
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
                    from_user=USER_IN_CHAT.format(
                        tag="from_user",
                        user_id=message.from_user_id,
                        **self._get_user_info(message.from_user),
                    ),
                    user_message=message.content,
                    content_type=(message.payload or {}).get("is_forwarded", False) and "forwarded-text" or "text",
                    reply_to_message=self._get_reply_to_message(message, messages),
                    date=message.created_at.isoformat(),
                ),
            }
        ]

    def _prepare_notification_message(
        self, message: Message, messages: list[Message]
    ) -> list[dict]:
        return [
            {
                "role": "user",
                "content": NOTIFICATION_MESSAGE_IN_CHAT.format(
                    notification_message=message.content,
                    date=message.created_at.isoformat(),
                ),
            }
        ]
