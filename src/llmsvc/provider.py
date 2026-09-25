import asyncio
from collections.abc import AsyncGenerator
from typing import Protocol


class Provider(Protocol):
    def stream(self, prompt: str, *, model: str) -> AsyncGenerator[str]: ...


class FakeProvider:
    def __init__(self) -> None:
        self.calls = 0

    async def stream(self, prompt: str, *, model: str) -> AsyncGenerator[str]:
        self.calls += 1
        for word in ["Hello", " from", " the", " fake", " provider."]:
            await asyncio.sleep(0.05)
            yield word
