"""Typed application settings with fail-fast validation.

Every variable from `.env.example` is mapped here; invalid or missing
configuration must stop the process at startup, never surface at runtime
(ARCHITECTURE.md §2, §12).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[3]

Environment = Literal["development", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]
LLMProviderName = Literal["mock", "dashscope"]


class SettingsError(RuntimeError):
    """Configuration is invalid or incomplete; the application must not start."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    sehat_env: Environment
    sehat_log_level: LogLevel = "INFO"
    sehat_db_path: Path = REPO_ROOT / "data" / "sehat.sqlite"

    # LLM provider (Alibaba Cloud Model Studio / DashScope)
    sehat_llm_provider: LLMProviderName = "mock"
    sehat_llm_model: str = "qwen-plus"
    sehat_llm_timeout: float = Field(default=30.0, gt=0)
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    # API server
    sehat_api_host: str = "127.0.0.1"
    sehat_api_port: int = Field(default=8000, ge=1, le=65535)
    sehat_cors_origins: str = "http://localhost:5173"

    # Behavior limits
    sehat_max_followup_rounds: int = Field(default=2, ge=0)
    sehat_max_message_chars: int = Field(default=2000, gt=0)

    @model_validator(mode="after")
    def _validate_provider_requirements(self) -> "Settings":
        if self.sehat_llm_provider == "dashscope" and not self.dashscope_api_key:
            raise ValueError(
                "DASHSCOPE_API_KEY is required when SEHAT_LLM_PROVIDER=dashscope"
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.sehat_cors_origins.split(",") if origin.strip()]


_UNSET: object = object()


def load_settings(env_file: str | Path | None | object = _UNSET) -> Settings:
    """Load and validate settings, converting validation failures into a
    single clear startup error. Pass env_file=None to skip any .env file."""
    kwargs: dict = {} if env_file is _UNSET else {"_env_file": env_file}
    try:
        return Settings(**kwargs)
    except ValidationError as exc:
        raise SettingsError(f"Invalid or missing configuration:\n{exc}") from exc


@lru_cache
def get_settings() -> Settings:
    return load_settings()
