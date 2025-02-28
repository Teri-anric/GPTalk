import inspect
from typing import Any
from pydantic import BaseModel, PrivateAttr


class BaseTool(BaseModel):
    __name__: str

    _extra_payload: dict = PrivateAttr(default_factory=dict)

    @property
    def extra_payload(self) -> dict:
        return self._extra_payload

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

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        self._extra_payload = data.pop("_extra_payload", {})
