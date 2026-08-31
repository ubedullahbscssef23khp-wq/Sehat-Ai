"""Offline scripted provider for tests and development (ARCHITECTURE.md §10).

Responses are consumed in order; an exhausted queue fails loudly instead of
inventing content, so degraded paths stay testable.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Sequence

from app.llm.provider import LLMUnavailableError
from app.llm.types import LLMRequest, LLMResponse

__all__ = ["MockProvider"]


class MockProvider:
    def __init__(self, scripts: Sequence[str] = (), model_name: str = "mock-provider") -> None:
        self.model_name = model_name
        self._queue: deque[str] = deque(scripts)
        self.requests: list[LLMRequest] = []

    async def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        if not self._queue:
            raise LLMUnavailableError("MockProvider has no scripted response remaining")
        return LLMResponse(model=self.model_name, text=self._queue.popleft())
