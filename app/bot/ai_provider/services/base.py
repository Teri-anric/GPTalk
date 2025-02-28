from abc import ABC, abstractmethod

from pydantic import BaseModel

from ..tools.base import BaseTool


class AiResponse(BaseModel):
    response: str
    tools: list[BaseTool]


class BaseAIService(ABC):
    @abstractmethod
    async def generate_response(
        self, prompt: str, messages: list[dict], tools: list[BaseTool]
    ) -> AiResponse:
        pass
