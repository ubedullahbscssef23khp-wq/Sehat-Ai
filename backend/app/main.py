"""Application factory.

Run locally with:
    python -m uvicorn app.main:create_app --factory

The factory (not module import) creates the app so configuration is loaded
exactly once at server startup and fails fast there (ARCHITECTURE.md §12).
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api import health
from app.core.config import Settings, load_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, request_id_ctx

logger = logging.getLogger("sehat.main")
access_logger = logging.getLogger("sehat.access")


class RequestIdMiddleware:
    """Assigns a request ID to each HTTP request, exposes it as the
    X-Request-ID response header, makes it available to log records, and
    emits one structured access-log line per request."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        token = request_id_ctx.set(request_id)
        status_code: int | str = "-"
        start = time.perf_counter()

        async def send_with_request_id(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", "-")
                headers = MutableHeaders(scope=message)
                headers.append("X-Request-ID", request_id)
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            duration_ms = (time.perf_counter() - start) * 1000
            access_logger.info(
                "%s %s -> %s (%.1f ms)",
                scope.get("method"),
                scope.get("path"),
                status_code,
                duration_ms,
                extra={"request_id": request_id},
            )
            request_id_ctx.reset(token)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or load_settings()
    configure_logging(settings.sehat_log_level)

    docs_config: dict[str, Any] = {}
    if settings.sehat_env == "production":
        # ARCHITECTURE.md §14: OpenAPI docs disabled in production mode.
        docs_config = {"docs_url": None, "redoc_url": None, "openapi_url": None}

    app = FastAPI(title="Sehat AI API", version="0.0.1", **docs_config)
    app.state.settings = settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestIdMiddleware)

    register_error_handlers(app)
    app.include_router(health.router)

    logger.info(
        "Sehat AI API ready env=%s provider=%s", settings.sehat_env, settings.sehat_llm_provider
    )
    return app
