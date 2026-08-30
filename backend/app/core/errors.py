"""Typed application errors and JSON error handlers.

Unhandled exceptions never leak internal details to clients; they are logged
(with request ID) and mapped to a stable error envelope.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("sehat.errors")


class SehatError(Exception):
    """Base for expected, typed application errors."""

    def __init__(self, message: str, *, code: str = "internal_error", status_code: int = 500) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(SehatError)
    async def handle_sehat_error(request: Request, exc: SehatError) -> JSONResponse:
        logger.warning("SehatError %s on %s %s: %s", exc.code, request.method, request.url.path, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "internal_error", "message": "An unexpected error occurred."}},
        )
