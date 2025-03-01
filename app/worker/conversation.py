import json
from app.constants import BASE_PROMPT, TEXT_MESSAGE_IN_CHAT, NOT_RESPONSE_TOOL_MESSAGE, USER_IN_CHAT, REPLY_TO_MESSAGE_IN_CHAT
from app.db import Message, MessageType
from datetime import datetime

class ConversationBuilder:
    def __init__(self, assistant_user_id: int):
        self.assistant_user_id = assistant_user_id


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
                    "content": json.dumps(tool_call_result),
                    "tool_call_id": tool_call["id"],
                }
            )
        return conversation

    def _get_reply_to_message(self, message: Message, messages: list[Message]) -> str:
        if message.reply_to_id is None:
            return ""
        reply_to_message = next((m for m in messages if m.telegram_id == message.reply_to_id), None)
        if reply_to_message is None:
            return ""
        return REPLY_TO_MESSAGE_IN_CHAT.format(
            reply_to_id=reply_to_message.telegram_id,
            reply_to_user=USER_IN_CHAT.format(
                tag="reply_to_user",
                user_id=reply_to_message.from_user_id,
                username=reply_to_message.from_user.username if reply_to_message.from_user else "",
                first_name=reply_to_message.from_user.first_name if reply_to_message.from_user else "",
                    last_name=reply_to_message.from_user.last_name if reply_to_message.from_user else "",
            ),
            reply_to_text=reply_to_message.content[:50],
        )


    def _prepare_message_text(self, message: Message, messages: list[Message]) -> list[dict]:
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
                        username=message.from_user.username if message.from_user else "",
                        first_name=message.from_user.first_name if message.from_user else "",
                        last_name=message.from_user.last_name if message.from_user else "",
                    ),
                    user_message=message.content,
                    reply_to_message=self._get_reply_to_message(message, messages),
                    date=message.created_at.strftime("%Y-%m-%d %H:%M:%S"),
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
                    current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            }
        ]
        for message in messages:    
            if message.type == MessageType.TOOL_CALLS:
                conversation.extend(self._prepare_tool_call_message(message))
            if message.type in (MessageType.AI_REFLECTION, MessageType.TEXT):
                conversation.extend(self._prepare_message_text(message, messages))
        return conversation


    def build(self, prompt: str, messages: list[Message]):
        return self._prepare_messages(prompt, messages)
