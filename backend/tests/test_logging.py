"""Structured JSON logging with request IDs (Phase 0 acceptance criterion 3)."""

from __future__ import annotations

import json
import logging

from app.core.logging import JsonFormatter, RequestIdFilter, request_id_ctx


def _make_record(message: str) -> logging.LogRecord:
    return logging.LogRecord(
        name="sehat.test", level=logging.INFO, pathname=__file__, lineno=1,
        msg=message, args=None, exc_info=None,
    )


def _format_with_filter(record: logging.LogRecord) -> dict:
    RequestIdFilter().filter(record)
    return json.loads(JsonFormatter().format(record))


def test_log_line_is_valid_json_with_core_fields() -> None:
    payload = _format_with_filter(_make_record("hello"))
    assert payload["level"] == "INFO"
    assert payload["logger"] == "sehat.test"
    assert payload["message"] == "hello"
    assert "timestamp" in payload


def test_log_line_omits_request_id_outside_request() -> None:
    payload = _format_with_filter(_make_record("no request"))
    assert "request_id" not in payload


def test_log_line_includes_request_id_inside_request() -> None:
    token = request_id_ctx.set("req-123")
    try:
        payload = _format_with_filter(_make_record("inside request"))
    finally:
        request_id_ctx.reset(token)
    assert payload["request_id"] == "req-123"


def test_exception_serialized_into_payload() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        import sys

        record = logging.LogRecord(
            name="sehat.test", level=logging.ERROR, pathname=__file__, lineno=1,
            msg="failed", args=None, exc_info=sys.exc_info(),
        )
    payload = _format_with_filter(record)
    assert "ValueError: boom" in payload["exception"]
