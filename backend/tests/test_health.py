"""API smoke tests (Phase 0 acceptance criterion 1) + request-id behavior."""

from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture()
def client() -> TestClient:
    settings = Settings(sehat_env="development", sehat_llm_provider="mock", _env_file=None)
    app = create_app(settings=settings)
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "sehat-ai"
    assert body["env"] == "development"
    assert body["llm_provider"] == "mock"


def test_response_carries_request_id_header(client: TestClient) -> None:
    response = client.get("/health")
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert len(request_id) == 32


def test_request_ids_are_unique_per_request(client: TestClient) -> None:
    first = client.get("/health").headers["X-Request-ID"]
    second = client.get("/health").headers["X-Request-ID"]
    assert first != second


def test_access_log_line_carries_request_id(client: TestClient, caplog: pytest.LogCaptureFixture) -> None:
    with caplog.at_level(logging.INFO, logger="sehat.access"):
        response = client.get("/health")
    request_id = response.headers["X-Request-ID"]
    access_records = [r for r in caplog.records if r.name == "sehat.access"]
    assert len(access_records) == 1
    record = access_records[0]
    assert "GET /health -> 200" in record.getMessage()
    assert getattr(record, "request_id", None) == request_id
