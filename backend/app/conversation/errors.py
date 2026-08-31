"""Typed conversation errors mapped by the existing error handlers."""

from __future__ import annotations

from app.core.errors import SehatError


class SessionNotFoundError(SehatError):
    def __init__(self, session_id: str) -> None:
        super().__init__(
            f"Session {session_id} was not found.",
            code="session_not_found",
            status_code=404,
        )


class SessionClosedError(SehatError):
    def __init__(self, session_id: str) -> None:
        super().__init__(
            f"Session {session_id} is closed and cannot accept messages.",
            code="session_closed",
            status_code=409,
        )
