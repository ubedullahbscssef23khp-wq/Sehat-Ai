"""Typed request/response models for LLM providers (ARCHITECTURE.md §10).

Providers are the only components that handle these wire types; the rest of
the application works with domain models, never provider-specific payloads.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

__all__ = ["LLMMessage", "LLMRequest", "LLMResponse"]


class LLMMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1)


class LLMRequest(BaseModel):
    model: str = Field(min_length=1)
    messages: list[LLMMessage] = Field(min_length=1)
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class LLMResponse(BaseModel):
    model: str = Field(min_length=1)
    text: str
