BASE_PROMPT = """
You responce to NOT SHOW FOR USERS, you can think and responce in any language, but you should use <user_instructions> to understand user instructions.
You can change your instructions in <user_instructions> tag using tool.
You can send message and other actions to user using tools.
Send response only to new messages.

<user_instructions>
{user_instructions}
</user_instructions>

<info>
    <current_time>UTC: {current_time}</current_time>
    <assistant_id>{assistant_id}</assistant_id>
</info>

<chat id="{chat_id}">
    <chat_type>{chat_type}</chat_type>
    <chat_title>{chat_title}</chat_title>
    <chat_username>{chat_username}</chat_username>

    <chat_messages>
    {chat_messages}
    </chat_messages>
</chat>
"""

SHORT_USER_IN_CHAT = """
<{tag} id="{user_id}" />
"""

TEXT_MESSAGE_CONTENT = """
<text>{content}</text>
"""

QUOTE_MESSAGE_CONTENT = """
<quote>{content}</quote>
"""

SHORT_TEXT_MESSAGE_CONTENT = """
<short_text>{content}</short_text>
"""

FORWARDED_TEXT_MESSAGE_CONTENT = """
<forwarded_text>{content}</forwarded_text>
"""

USER_IN_CHAT = """
<{tag} id="{user_id}" >
    <username>{username}</username>
    <first_name>{first_name}</first_name>
    <last_name>{last_name}</last_name>
</{tag}>
"""

EXTERNAL_REPLY_IN_CHAT = """
<external_reply id="{reply_to_id}">
    {reply_to_user}
    {content}
</external_reply>
"""

REPLY_TO_MESSAGE_IN_CHAT = """
<reply_to id="{reply_to_id}">
    {reply_to_user}
    <{reply_type_content}>{reply_to_content}</{reply_type_content}>
</reply_to>
"""

TEXT_MESSAGE_IN_CHAT = """
<message id="{message_id}" class_name="{class_name}">
    {from_user}
    {content}
    {reply_to_message}
    <date>{date}</date>
</message>
"""

NOTIFICATION_MESSAGE_IN_CHAT = """
<NOTIFICATION>
    <date>{date}</date>
    <message>{notification_message}</message>
</NOTIFICATION>
"""

TOOL_IN_CHAT = """
<tool>
    <name>{tool_name}</name>
    <parameters>{tool_parameters}</parameters>
    <result>{tool_result}</result>
</tool>
"""

AI_REFLECTION_MESSAGE_IN_CHAT = """
<ai_reflection>
    {content}
</ai_reflection>
"""

NOT_RESPONSE_TOOL_MESSAGE = "**Tool call empty response**"
