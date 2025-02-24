import inspect

from pydantic import BaseModel


class BaseTool(BaseModel):
    __name__: str

    __tool_call_id: str

    @property
    def tool_call_id(self) -> str:
        return self.__tool_call_id

    @tool_call_id.setter
    def tool_call_id(self, value: str):
        self.__tool_call_id = value

    async def __call__(self):
        pass

    async def run(self, context: dict):
        kwargs = self._prepare_kwargs(context)
        await self(**kwargs)

    def _prepare_kwargs(self, kwargs: dict) -> dict:
        spec = inspect.getfullargspec(self.__call__)
        params = {*spec.args, *spec.kwonlyargs}
        varkw = spec.varkw is not None

        if varkw:
            return kwargs

        return {k: kwargs[k] for k in params if k in kwargs}
