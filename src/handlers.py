import inspect
import asyncio
from abc import ABC, abstractmethod

import aiohttp


def get_handler_class(class_name: str) -> "Handler":
    if obj := globals().get(class_name):
        if inspect.isclass(obj):
            if issubclass(obj, Handler):
                if obj is not Handler:
                    return obj
    raise ValueError(class_name)


class Handler(ABC):
    @abstractmethod
    async def process(self) -> None:
        raise NotImplementedError()


class PortAvailability(Handler):
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    async def process(self) -> None:
        _reader, writer = await asyncio.open_connection(self._host, self._port)
        writer.close()
        await writer.wait_closed()


class WebAvailability(Handler):
    def __init__(
        self, url: str, result_text: str | None = None,
        result_json: dict | None = None
    ):
        self._url = url
        self._result_text = result_text
        self._result_json = result_json

    async def process(self) -> None:
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(self._url) as resp:
                if self._result_text is not None:
                    resp_text = await resp.text()
                    assert resp_text == self._result_text, resp_text
                if self._result_json is not None:
                    resp_json = await resp.json()
                    assert resp_json == self._result_json, resp_json
