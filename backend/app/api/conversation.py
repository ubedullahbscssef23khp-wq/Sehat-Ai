"""Conversation endpoints — thin HTTP layer over the orchestrator (ARCHITECTURE.md §4).

All decision logic lives in the orchestrator and the deterministic safety core;
these handlers only validate input at the boundary and translate typed errors.
"""

from __future__ import annotations

from typing import cast

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.conversation.errors import SessionNotFoundError
from app.conversation.orchestrator import ConversationOrchestrator
from app.core.config import Settings
from app.core.errors import SehatError
from app.llm.provider import LLMUnavailableError
from app.models import GuidanceResponse, Language, Session

router = APIRouter(prefix="/sessions", tags=["conversation"])


class CreateSessionRequest(BaseModel):
    preferred_language: Language = Language.EN


class SendMessageRequest(BaseModel):
    text: str = Field(min_length=1)


class MessageTooLongError(SehatError):
    def __init__(self, max_chars: int) -> None:
        super().__init__(
            f"Message text must be at most {max_chars} characters.",
            code="message_too_long",
            status_code=422,
        )


class MessageEmptyError(SehatError):
    def __init__(self) -> None:
        super().__init__(
            "Message text must not be blank.", code="message_empty", status_code=422
        )


class LLMUnavailableAPIError(SehatError):
    def __init__(self) -> None:
        super().__init__(
            "The guidance service is temporarily unavailable. Please try again shortly.",
            code="llm_unavailable",
            status_code=503,
        )


def _orchestrator(request: Request) -> ConversationOrchestrator:
    return cast(ConversationOrchestrator, request.app.state.orchestrator)


def _settings(request: Request) -> Settings:
    return cast(Settings, request.app.state.settings)


@router.post("", status_code=201)
def create_session(payload: CreateSessionRequest, request: Request) -> Session:
    return _orchestrator(request).create_session(payload.preferred_language)


@router.get("/{session_id}")
def get_session(session_id: str, request: Request) -> Session:
    session = _orchestrator(request).get_session(session_id)
    if session is None:
        raise SessionNotFoundError(session_id)
    return session


@router.post("/{session_id}/messages")
async def post_message(
    session_id: str, payload: SendMessageRequest, request: Request
) -> GuidanceResponse:
    text = payload.text.strip()
    if not text:
        raise MessageEmptyError()
    if len(text) > _settings(request).sehat_max_message_chars:
        raise MessageTooLongError(_settings(request).sehat_max_message_chars)
    try:
        return await _orchestrator(request).handle_message(session_id, text)
    except LLMUnavailableError:
        raise LLMUnavailableAPIError() from None
