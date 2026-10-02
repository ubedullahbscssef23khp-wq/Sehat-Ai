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
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import sessionmaker
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api import conversation, health, v1
from app.conversation.orchestrator import ConversationOrchestrator
from app.core.config import Settings, load_settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging, request_id_ctx
from app.knowledge.loader import load_entries_dir
from app.knowledge.paths import CONTENT_DIR
from app.llm.provider import build_provider
from app.persistence.database import build_engine, init_db
from app.safety.loader import load_patterns_dir, load_rules_dir
from app.safety.paths import PRESCREEN_DIR, RULES_DIR

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


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "DENY")
                headers.append("Referrer-Policy", "strict-origin-when-cross-origin")
                headers.append("Permissions-Policy", "camera=(), geolocation=(), microphone=(self), payment=()")
                headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
                headers.append(
                    "Content-Security-Policy",
                    "default-src 'self'; "
                    "script-src 'self'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data:; "
                    "font-src 'self' data:; "
                    "connect-src 'self' https://generativelanguage.googleapis.com; "
                    "object-src 'none'; "
                    "base-uri 'self'; "
                    "frame-ancestors 'none';"
                )
            await send(message)

        await self.app(scope, receive, send_with_headers)


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
    app.add_middleware(SecurityHeadersMiddleware)

    register_error_handlers(app)
    app.include_router(health.router)

    engine = build_engine(settings.sehat_db_path)
    init_db(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    orchestrator = ConversationOrchestrator(
        provider=build_provider(settings),
        session_factory=session_factory,
        rules=load_rules_dir(RULES_DIR),
        prescreen_patterns=load_patterns_dir(PRESCREEN_DIR),
        max_followup_rounds=settings.sehat_max_followup_rounds,
        knowledge=load_entries_dir(CONTENT_DIR),
    )
    app.state.orchestrator = orchestrator
    app.include_router(conversation.router)
    app.include_router(v1.router)

    # Production Static Asset Serving
    dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "dist")
    if os.path.isdir(dist_path):
        class ImmutableStaticFiles(StaticFiles):
            async def get_response(self, path: str, scope: Scope):
                response = await super().get_response(path, scope)
                response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
                return response

        app.mount("/assets", ImmutableStaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
        
        @app.get("/{catchall:path}", include_in_schema=False)
        def serve_spa(catchall: str):
            # Exclude /api routes from being caught
            if catchall.startswith("api/") or catchall.startswith("v1/"):
                return {"detail": "Not Found"}
            return FileResponse(
                os.path.join(dist_path, "index.html"),
                headers={"Cache-Control": "no-cache, must-revalidate"}
            )

    logger.info(
        "Sehat AI API ready env=%s provider=%s", settings.sehat_env, settings.sehat_llm_provider
    )
    return app
