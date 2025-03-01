BASE_PROMPT = """
You are an AI assistant that executes actions using tools.
Provided text-based result not show for users, exept some tools.

<instructions>
**Execute the required tool immediately** if an action is needed.  
**If no tool is required, remain silent** and do nothing.  
**Follow any user-specific instructions for tool execution**.
</instructions>

<current_time>
{current_time}
</current_time>

<user_instructions>
{user_instructions}
</user_instructions>
"""

USER_IN_CHAT = """
<{tag} id="{user_id}" >
    <username>{username}</username>
    <first_name>{first_name}</first_name>
    <last_name>{last_name}</last_name>
</{tag}>
"""

REPLY_TO_MESSAGE_IN_CHAT = """
<reply_to id="{reply_to_id}">
    {reply_to_user}
    <short-text>{reply_to_text}</short-text>
</reply_to>
"""

TEXT_MESSAGE_IN_CHAT = """
<message id="{message_id}">
    {from_user}
    <text>{user_message}</text>
    <date>{date}</date>
    {reply_to_message}
</message>
"""

NOT_RESPONSE_TOOL_MESSAGE = "**Tool call empty response**"
