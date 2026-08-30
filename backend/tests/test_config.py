"""Fail-fast configuration validation (Phase 0 acceptance criterion 2)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings, SettingsError, load_settings

ENV_VARS = [
    "SEHAT_ENV",
    "SEHAT_LOG_LEVEL",
    "SEHAT_DB_PATH",
    "SEHAT_LLM_PROVIDER",
    "SEHAT_LLM_MODEL",
    "SEHAT_LLM_TIMEOUT",
    "DASHSCOPE_API_KEY",
    "DASHSCOPE_BASE_URL",
    "SEHAT_API_HOST",
    "SEHAT_API_PORT",
    "SEHAT_CORS_ORIGINS",
    "SEHAT_MAX_FOLLOWUP_ROUNDS",
    "SEHAT_MAX_MESSAGE_CHARS",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)


def make_settings(**overrides) -> Settings:
    base: dict = {"sehat_env": "development", "sehat_llm_provider": "mock", "_env_file": None}
    base.update(overrides)
    return Settings(**base)


def test_minimal_valid_settings() -> None:
    settings = make_settings()
    assert settings.sehat_env == "development"
    assert settings.sehat_llm_provider == "mock"
    assert settings.sehat_api_port == 8000
    assert settings.sehat_log_level == "INFO"


def test_missing_required_env_fails_fast(monkeypatch: pytest.MonkeyPatch) -> None:
    # env_file=None: no .env is read and SEHAT_ENV is unset, so startup must fail.
    with pytest.raises(SettingsError):
        load_settings(env_file=None)


def test_invalid_environment_value_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(sehat_env="staging")


def test_invalid_provider_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(sehat_llm_provider="openai")


def test_invalid_log_level_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(sehat_log_level="VERBOSE")


def test_dashscope_provider_requires_api_key() -> None:
    with pytest.raises(ValidationError, match="DASHSCOPE_API_KEY"):
        make_settings(sehat_llm_provider="dashscope", dashscope_api_key="")


def test_dashscope_provider_with_key_ok() -> None:
    settings = make_settings(sehat_llm_provider="dashscope", dashscope_api_key="dummy")
    assert settings.sehat_llm_provider == "dashscope"


def test_cors_origins_parsed_to_list() -> None:
    settings = make_settings(sehat_cors_origins="http://a.test, http://b.test ,,")
    assert settings.cors_origin_list == ["http://a.test", "http://b.test"]


def test_invalid_port_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(sehat_api_port=70000)


def test_non_positive_limits_rejected() -> None:
    with pytest.raises(ValidationError):
        make_settings(sehat_max_message_chars=0)
