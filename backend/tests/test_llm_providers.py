"""LLM provider tests (Phase 2).

Covers MockProvider offline behavior, DashScopeProvider request/response
handling via injected httpx transports (no network), provider selection from
settings, and the environment-only API key invariant.
"""

from __future__ import annotations

import asyncio
import json
import re
from pathlib import Path

import httpx
import pytest

from app.core.config import Settings
from app.llm.dashscope import DashScopeProvider
from app.llm.mock import MockProvider
from app.llm.provider import LLMProvider, LLMUnavailableError, build_provider
from app.llm.types import LLMMessage, LLMRequest

PLACEHOLDER_KEY = "test-placeholder-key-not-a-real-secret"


def _request(content: str = "hello") -> LLMRequest:
    return LLMRequest(model="qwen-plus", messages=[LLMMessage(role="user", content=content)])


def _openai_body(text: str, model: str = "qwen-plus") -> dict:
    return {"model": model, "choices": [{"message": {"role": "assistant", "content": text}}]}


def _dashscope(handler) -> DashScopeProvider:
    return DashScopeProvider(
        api_key=PLACEHOLDER_KEY,
        base_url="https://llm.example.test/v1",
        model="qwen-plus",
        timeout=5.0,
        transport=httpx.MockTransport(handler),
    )


# --- MockProvider ---------------------------------------------------------


def test_mock_provider_returns_scripted_responses_in_order() -> None:
    provider = MockProvider(scripts=["first", "second"])
    first = asyncio.run(provider.complete(_request()))
    second = asyncio.run(provider.complete(_request()))
    assert first.text == "first"
    assert second.text == "second"
    assert provider.requests[0].messages[-1].content == "hello"


def test_mock_provider_exhausted_queue_raises_unavailable() -> None:
    provider = MockProvider(scripts=["only-one"])
    asyncio.run(provider.complete(_request()))
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_mock_provider_echoes_model_name() -> None:
    response = asyncio.run(MockProvider(scripts=["x"]).complete(_request()))
    assert response.model == "mock-provider"


# --- Provider selection from settings --------------------------------------


def test_build_provider_defaults_to_mock() -> None:
    settings = Settings(sehat_env="development", sehat_llm_provider="mock", _env_file=None)
    provider = build_provider(settings)
    assert isinstance(provider, MockProvider)
    assert isinstance(provider, LLMProvider)


def test_build_provider_selects_dashscope() -> None:
    settings = Settings(
        sehat_env="development",
        sehat_llm_provider="dashscope",
        dashscope_api_key=PLACEHOLDER_KEY,
        _env_file=None,
    )
    provider = build_provider(settings)
    assert isinstance(provider, DashScopeProvider)
    assert provider.model_name == settings.sehat_llm_model


# --- DashScopeProvider -----------------------------------------------------


def test_dashscope_request_shape_and_auth_header() -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["request"] = request
        return httpx.Response(200, json=_openai_body("ok"))

    provider = _dashscope(handler)
    response = asyncio.run(provider.complete(_request("user text")))

    sent = captured["request"]
    assert str(sent.url) == "https://llm.example.test/v1/chat/completions"
    assert sent.headers["authorization"] == f"Bearer {PLACEHOLDER_KEY}"
    payload = json.loads(sent.content)
    assert payload["model"] == "qwen-plus"
    assert payload["messages"][-1] == {"role": "user", "content": "user text"}
    assert response.text == "ok"
    assert response.model == "qwen-plus"


def test_dashscope_non_200_raises_unavailable() -> None:
    provider = _dashscope(lambda request: httpx.Response(503, json={}))
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_dashscope_malformed_body_raises_unavailable() -> None:
    provider = _dashscope(lambda request: httpx.Response(200, json={"unexpected": True}))
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_dashscope_empty_content_raises_unavailable() -> None:
    provider = _dashscope(lambda request: httpx.Response(200, json=_openai_body("   ")))
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_dashscope_network_error_raises_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = _dashscope(handler)
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_dashscope_timeout_raises_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("read timed out")

    provider = _dashscope(handler)
    with pytest.raises(LLMUnavailableError):
        asyncio.run(provider.complete(_request()))


def test_dashscope_rejects_empty_api_key() -> None:
    with pytest.raises(ValueError, match="DASHSCOPE_API_KEY"):
        DashScopeProvider(
            api_key="", base_url="https://llm.example.test/v1", model="qwen-plus", timeout=5.0
        )


# --- Environment-only key invariant -----------------------------------------


def test_no_hardcoded_api_keys_in_backend_sources() -> None:
    """API keys come only from the environment: nothing key-like may be
    embedded in application source or prompt text (Phase 2 acceptance)."""
    app_root = Path(__file__).resolve().parents[1] / "app"
    pattern = re.compile(r"sk-[A-Za-z0-9_-]{16,}|Bearer\s+[A-Za-z0-9_-]{24,}")
    offenders = []
    for path in app_root.rglob("*.py"):
        if pattern.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path))
    assert offenders == []
