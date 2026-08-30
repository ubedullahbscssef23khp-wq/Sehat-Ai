"""Health endpoint — thin, no business logic (ARCHITECTURE.md §4)."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.core.config import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
def get_health(request: Request) -> dict[str, str]:
    settings: Settings = request.app.state.settings
    return {
        "status": "ok",
        "service": "sehat-ai",
        "env": settings.sehat_env,
        "llm_provider": settings.sehat_llm_provider,
    }
