from .services import OpenAIService, BaseAIService


class AIProvider:
    def get_ai_service(self, service_name: str) -> BaseAIService | None:
        provider, model = service_name.split("/")
        if provider == "openai":
            return OpenAIService(model)
        return None
