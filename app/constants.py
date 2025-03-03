BASE_PROMPT = """
You responce to NOT SHOW FOR USERS, you can think and responce in any language, but you should use <user_instructions> to understand user instructions.
You can change your instructions in <user_instructions> tag using tool.
You can send message and other actions to user using tools.

<user_instructions>
{user_instructions}
</user_instructions>

<current_time>
UTC: {current_time}
</current_time>
<chat id="{chat_id}">
    <chat_type>{chat_type}</chat_type>
    <chat_title>{chat_title}</chat_title>
    <chat_username>{chat_username}</chat_username>
</chat>

Chat Structure:
old messsage
middle message
new message
"""

SHORT_USER_IN_CHAT = """
<{tag} id="{user_id}" />
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
    <{reply_type_content}>{reply_to_content}</{reply_type_content}>
</external_reply>
"""

REPLY_TO_MESSAGE_IN_CHAT = """
<reply_to id="{reply_to_id}">
    {reply_to_user}
    <{reply_type_content}>{reply_to_content}</{reply_type_content}>
</reply_to>
"""

TEXT_MESSAGE_IN_CHAT = """
<message id="{message_id}">
    {from_user}
    <{content_type}>{user_message}</{content_type}>
    {reply_to_message}
    <date>{date}</date>
</message>
"""

NOTIFICATION_MESSAGE_IN_CHAT = """
<NOTIFICATION>
    <date>{date}</date>
    <text>{notification_message}</text>
</NOTIFICATION>
"""

NOT_RESPONSE_TOOL_MESSAGE = "**Tool call empty response**"
