"""LLM provider abstraction (ARCHITECTURE.md §10).

This module family is the only one allowed to talk to a model. Providers are
swappable behind the LLMProvider protocol; selection comes from settings, so
changing models is a configuration change, not a code change.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

from app.llm.types import LLMRequest, LLMResponse

if TYPE_CHECKING:
    from app.core.config import Settings

__all__ = ["LLMProvider", "LLMUnavailableError", "build_provider"]


class LLMUnavailableError(RuntimeError):
    """The LLM backend is unreachable, failed, or returned an unusable answer."""


@runtime_checkable
class LLMProvider(Protocol):
    model_name: str

    async def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete the request or raise LLMUnavailableError."""
        ...


def build_provider(settings: Settings) -> LLMProvider:
    """Instantiate the provider selected by settings (fail fast on misconfiguration)."""
    if settings.sehat_llm_provider == "mock":
        from app.llm.mock import MockProvider

        return MockProvider()
    from app.llm.dashscope import DashScopeProvider

    return DashScopeProvider(
        api_key=settings.dashscope_api_key,
        base_url=settings.dashscope_base_url,
        model=settings.sehat_llm_model,
        timeout=settings.sehat_llm_timeout,
    )
