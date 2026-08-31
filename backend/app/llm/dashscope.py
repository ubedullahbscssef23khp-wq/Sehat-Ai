"""DashScope provider via the OpenAI-compatible HTTP endpoint (ARCHITECTURE.md §10).

Direct httpx calls — no SDK/framework (decision D3). The API key arrives only
as a constructor argument sourced from settings (environment); it is never
logged and never embedded in prompts or code.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.llm.provider import LLMUnavailableError
from app.llm.types import LLMRequest, LLMResponse

__all__ = ["DashScopeProvider"]


class DashScopeProvider:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        model: str,
        timeout: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        if not api_key:
            raise ValueError(
                "DashScope API key is empty; set DASHSCOPE_API_KEY in the environment"
            )
        self.model_name = model
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers={"Authorization": f"Bearer {api_key}"},
            transport=transport,
        )

    async def complete(self, request: LLMRequest) -> LLMResponse:
        payload: dict[str, Any] = {
            "model": request.model,
            "messages": [message.model_dump() for message in request.messages],
            "temperature": request.temperature,
        }
        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.HTTPError as exc:
            raise LLMUnavailableError(f"LLM request failed: {type(exc).__name__}") from exc
        if response.status_code != 200:
            raise LLMUnavailableError(f"LLM request failed with HTTP {response.status_code}")
        try:
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        except (TypeError, KeyError, IndexError, ValueError) as exc:
            raise LLMUnavailableError("LLM response was malformed") from exc
        if not isinstance(content, str) or not content.strip():
            raise LLMUnavailableError("LLM response contained no usable text")
        model = data.get("model") or request.model
        return LLMResponse(model=str(model), text=content)

    async def aclose(self) -> None:
        await self._client.aclose()
