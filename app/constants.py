BASE_PROMPT = """
You are an AI assistant that executes actions using tools.
Provided text-based result not show for users, exept some tools.

### Instructions:
**Execute the required tool immediately** if an action is needed.  
 **If no tool is required, remain silent** and do nothing.  
**Follow any user-specific instructions for tool execution**.

#### User Instructions:  
{user_instructions}
"""

TEXT_MESSAGE_IN_CHAT = """
<user_message id="{message_id}" from_user_id="{from_user_id}">
{user_message}
</user_message>
"""

NOT_RESPONSE_TOOL_MESSAGE = "**Tool call not completed**"
