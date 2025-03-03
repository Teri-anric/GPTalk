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
    TOOL_IN_CHAT,
    TEXT_MESSAGE_CONTENT,
    SHORT_TEXT_MESSAGE_CONTENT,
    QUOTE_MESSAGE_CONTENT,
    FORWARDED_TEXT_MESSAGE_CONTENT,
    AI_REFLECTION_MESSAGE_IN_CHAT,
)
from app.db import Message, MessageType, User, Chat
from datetime import datetime


class ConversationBuilder:
    def __init__(self, assistant_user_id: int):
        self.assistant_user_id = assistant_user_id

    def build(self, chat: Chat, messages: list[Message], last_seen_date: datetime):
        return self._prepare_messages(chat, messages, last_seen_date)

    def _prepare_messages(self, chat: Chat, messages: list[Message], last_seen_date: datetime) -> list[dict]:
        conversation = []
        for message in messages:
            if message.type == MessageType.TOOL_CALLS:
                conversation.extend(self._prepare_tool_call_message(message))
            if message.type == MessageType.TEXT:
                conversation.extend(self._prepare_message_text(message, messages, last_seen_date))
            if message.type == MessageType.AI_REFLECTION:
                conversation.extend(self._prepare_ai_reflection_message(message, messages))
            if message.type == MessageType.NOTIFICATION:
                conversation.extend(
                    self._prepare_notification_message(message, messages)
                )
        return [
            {
                "role": "system",
                "content": BASE_PROMPT.format(
                    user_instructions=chat.ai_settings.prompt,
                    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    chat_id=chat.id,
                    chat_type=chat.type,
                    chat_title=chat.title,
                    chat_username=chat.username,
                    chat_messages="\n".join(conversation),
                    assistant_id=self.assistant_user_id,
                ),
            }
        ]
    
    def _prepare_ai_reflection_message(self, message: Message, messages: list[Message]) -> list[str]:
        return [
            AI_REFLECTION_MESSAGE_IN_CHAT.format(
                content=message.content,
            )
        ]

    def _prepare_tool_call_message(self, message: Message) -> list[str]:
        tool_calls = message.payload["tool_calls"]
        tool_calls_results = message.payload["tool_calls_results"]
        conversation = []

        for tool_call in tool_calls:
            tool_call_result = (
                tool_calls_results[tool_call["id"]] or NOT_RESPONSE_TOOL_MESSAGE
            )
            conversation.append(
                TOOL_IN_CHAT.format(
                    tool_name=tool_call["function"]["name"],
                    tool_parameters=tool_call["function"]["arguments"],
                    tool_result=json.dumps(tool_call_result),
                )
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
        
        content_template = TEXT_MESSAGE_CONTENT
        reply_to_content = reply_to.get("content")
        if len(reply_to_content) > 50:
            content_template = SHORT_TEXT_MESSAGE_CONTENT
            reply_to_content = reply_to_content[:50] + "..."
        if reply_to.get("type") == "quote":
            content_template = QUOTE_MESSAGE_CONTENT

        reply_to_user = self._get_reply_to_user(message, messages)
        if reply_to.get("type") == "external":
            return EXTERNAL_REPLY_IN_CHAT.format(
                reply_to_id=reply_to.get("id"),
                reply_to_user=reply_to_user,
                content=content_template.format(content=reply_to_content),
            )
        return REPLY_TO_MESSAGE_IN_CHAT.format(
            reply_to_id=reply_to.get("id"),
            reply_to_user=reply_to_user,
            content=content_template.format(content=reply_to_content),
        )

    def _prepare_message_content(self, message: Message, messages: list[Message]) -> str:
        content = ""
        current_index = messages.index(message)
        while current_index > 0:
            message = messages[current_index]
            payload = message.payload or {}
            if payload.get("is_forwarded", False):
                content += FORWARDED_TEXT_MESSAGE_CONTENT.format(content=message.content)
                content += "\n"
            else:
                content += TEXT_MESSAGE_CONTENT.format(content=message.content)
                content += "\n"
            current_index += 1
            if current_index >= len(messages):
                break
            if messages[current_index].from_user_id == message.from_user_id:
                messages.pop(current_index - 1)
                current_index -= 1
                continue
            break
        return content

    def _prepare_message_text(
        self, message: Message, messages: list[Message], last_seen_date: datetime
    ) -> list[str]:
        if not message.content:
            return []

        return [
            TEXT_MESSAGE_IN_CHAT.format(
                message_id=message.telegram_id,
                from_user_id=message.from_user_id,
                from_user=USER_IN_CHAT.format(
                    tag="from_user",
                    user_id=message.from_user_id,
                    **self._get_user_info(message.from_user),
                ),
                content=TEXT_MESSAGE_CONTENT.format(
                    content=message.content,
                    content_type=(message.payload or {}).get("is_forwarded", False) and "forwarded-text" or "text",
                ),
                reply_to_message=self._get_reply_to_message(message, messages),
                date=message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                class_name=message.created_at < last_seen_date and "new" or "old",
            )
        ]

    def _prepare_notification_message(
        self, message: Message, messages: list[Message]
    ) -> list[str]:
        return [
            NOTIFICATION_MESSAGE_IN_CHAT.format(
                notification_message=message.content,
                date=message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ),
        ]
