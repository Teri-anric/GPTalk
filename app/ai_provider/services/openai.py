import json
from json.decoder import JSONDecodeError
import logging

from openai import OpenAI
from openai.lib import pydantic_function_tool
from openai.types.chat import ChatCompletion

from app.config import settings

from ..tools.base import BaseTool
from .base import AiResponse, BaseAIService

logger = logging.getLogger(__name__)


class OpenAIService(BaseAIService):
    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = model

    def tools_to_openai(self, tools: list[BaseTool]) -> list[dict] | None:
        return [pydantic_function_tool(tool) for tool in tools] or None

    def extract_tools(
        self, response: ChatCompletion, tools: list[BaseTool] | None = None
    ) -> list[BaseTool]:
        if tools is None:
            return []
        if response.choices[0].message.tool_calls is None:
            return []

        tools_map = {tool.__name__: tool for tool in tools}

        tools = []
        for tool in response.choices[0].message.tool_calls:
            tool_cls = tools_map.get(tool.function.name)
            if tool_cls is None:
                continue
            try:
                tools.append(
                    tool_cls(
                        **json.loads(tool.function.arguments),
                        _extra_payload=tool.model_dump(),
                    )
                )
            except JSONDecodeError as e:
                logger.error(f"Error creating tool {tool.function.name} with arguments {tool.function.arguments}: {e}")
                continue

        return tools
    
    async def generate_response(
        self, messages: list[dict], tools: list[BaseTool]
    ) -> AiResponse:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tools_to_openai(tools),
            tool_choice="auto",
        )

        return AiResponse(
            response=response.choices[0].message.content,
            tools=self.extract_tools(response, tools),
        )
