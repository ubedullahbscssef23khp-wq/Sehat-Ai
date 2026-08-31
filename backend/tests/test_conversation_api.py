"""Conversation API end-to-end tests (Phase 3 acceptance criteria).

All conversations use synthetic fixtures and the MockProvider; no medical
content and no real LLM calls are involved.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

from app.core.config import Settings
from app.conversation.orchestrator import ConversationOrchestrator
from app.llm.mock import MockProvider
from app.main import create_app
from app.models import SafetyLevel
from app.persistence.database import build_engine
from app.persistence.repositories import MessageRepository

from conversation_support import (
    case_json,
    incomplete_case_json,
    make_pattern,
    make_signal_rule,
    questions_json,
)


def make_settings(db_path: Path) -> Settings:
    return Settings(
        sehat_env="development",
        sehat_llm_provider="mock",
        sehat_db_path=db_path,
        _env_file=None,
    )


def inject_orchestrator(
    app: FastAPI,
    settings: Settings,
    scripts: tuple[str, ...] = (),
    rules: list | None = None,
    patterns: list | None = None,
) -> MockProvider:
    """Replace the bare mock orchestrator with one over a scripted provider,
    sharing the same SQLite file (simulates deployment configuration)."""
    provider = MockProvider(scripts)
    engine = build_engine(settings.sehat_db_path)
    session_factory: sessionmaker[SASession] = sessionmaker(
        bind=engine, expire_on_commit=False, future=True
    )
    app.state.orchestrator = ConversationOrchestrator(
        provider=provider,
        session_factory=session_factory,
        rules=rules or [],
        prescreen_patterns=patterns or [],
        max_followup_rounds=settings.sehat_max_followup_rounds,
    )
    return provider


@pytest.fixture()
def app_and_client(tmp_path: Path) -> Iterator[tuple[FastAPI, TestClient, Settings]]:
    settings = make_settings(tmp_path / "api.sqlite")
    app = create_app(settings=settings)
    with TestClient(app) as client:
        yield app, client, settings


def create_session(client: TestClient) -> str:
    response = client.post("/sessions", json={})
    assert response.status_code == 201
    session_id = response.json()["id"]
    assert session_id
    return session_id


def send_message(client: TestClient, session_id: str, text: str):
    return client.post(f"/sessions/{session_id}/messages", json={"text": text})


# ---------------------------------------------------------------------------
# Acceptance (a): multi-turn API conversation reaches a triage decision
# ---------------------------------------------------------------------------


def test_multi_turn_conversation_reaches_triage(app_and_client) -> None:
    app, client, settings = app_and_client
    provider = inject_orchestrator(
        app,
        settings,
        scripts=(incomplete_case_json(), questions_json(1), case_json()),
    )

    session_id = create_session(client)

    first = send_message(client, session_id, "synthetic first message")
    assert first.status_code == 200
    body = first.json()
    assert body["session_id"] == session_id
    assert body["triage"]["level"] == "needs_more_info"
    assert len(body["follow_up_questions"]) == 1
    assert body["disclaimers"], "mandatory disclaimers must be present"
    assert client.get(f"/sessions/{session_id}").json()["status"] == "collecting"

    second = send_message(client, session_id, "synthetic second message")
    assert second.status_code == 200
    body = second.json()
    assert body["triage"]["level"] == "self_care"
    assert body["triage"]["limited_confidence"] is False
    assert body["follow_up_questions"] == []
    assert body["disclaimers"], "mandatory disclaimers must be present"
    assert client.get(f"/sessions/{session_id}").json()["status"] == "guided"

    # The deterministic pipeline made exactly one extraction call per turn
    # and one phrasing call; no other LLM traffic occurred.
    assert len(provider.requests) == 3


# ---------------------------------------------------------------------------
# Acceptance (b): max 2 follow-up rounds, then best-effort limited confidence
# ---------------------------------------------------------------------------


def test_two_followup_rounds_then_best_effort(app_and_client) -> None:
    app, client, settings = app_and_client
    inject_orchestrator(
        app,
        settings,
        scripts=(
            incomplete_case_json(),
            "not json",  # phrasing falls back deterministically
            incomplete_case_json(),
            "not json",
            incomplete_case_json(),
        ),
    )
    session_id = create_session(client)

    for turn in (1, 2):
        response = send_message(client, session_id, f"synthetic message {turn}")
        assert response.status_code == 200
        body = response.json()
        assert body["triage"]["level"] == "needs_more_info"
        assert len(body["follow_up_questions"]) == 1

    final = send_message(client, session_id, "synthetic message 3")
    assert final.status_code == 200
    body = final.json()
    assert body["follow_up_questions"] == []
    assert body["triage"]["level"] != "needs_more_info"
    assert body["triage"]["limited_confidence"] is True
    assert client.get(f"/sessions/{session_id}").json()["status"] == "guided"


# ---------------------------------------------------------------------------
# Acceptance (d): emergency pre-screen shortcuts the loop, no LLM needed
# ---------------------------------------------------------------------------


def test_emergency_prescreen_shortcuts_without_llm(app_and_client) -> None:
    app, client, settings = app_and_client
    provider = inject_orchestrator(app, settings, patterns=[make_pattern()])
    session_id = create_session(client)

    response = send_message(client, session_id, "please help: SYNTHETIC-CHEST-PAIN")
    assert response.status_code == 200
    body = response.json()
    assert body["triage"]["level"] == "emergency"
    assert body["triage"]["fired_rule_ids"] == ["T-PRESCREEN-1"]
    assert body["follow_up_questions"] == []
    assert body["disclaimers"]
    assert provider.requests == []
    assert client.get(f"/sessions/{session_id}").json()["status"] == "escalated"


def test_deterministic_rule_escalation_via_api(app_and_client) -> None:
    app, client, settings = app_and_client
    payload = json.loads(incomplete_case_json())
    payload["red_flag_signals"] = ["synthetic_flag"]
    inject_orchestrator(
        app,
        settings,
        scripts=(json.dumps(payload),),
        rules=[make_signal_rule("T-RULE-1", "synthetic_flag", SafetyLevel.URGENT)],
    )
    session_id = create_session(client)
    response = send_message(client, session_id, "synthetic message")
    assert response.status_code == 200
    body = response.json()
    assert body["triage"]["level"] == "urgent_same_day"
    assert body["follow_up_questions"] == []
    assert client.get(f"/sessions/{session_id}").json()["status"] == "escalated"


# ---------------------------------------------------------------------------
# Acceptance (c): session state survives a server restart (SQLite-backed)
# ---------------------------------------------------------------------------


def test_session_state_survives_server_restart(tmp_path: Path) -> None:
    db_path = tmp_path / "restart.sqlite"
    settings = make_settings(db_path)

    first_app = create_app(settings=settings)
    with TestClient(first_app) as first:
        provider = inject_orchestrator(
            first_app, settings, scripts=(incomplete_case_json(), questions_json(1))
        )
        session_id = create_session(first)
        response = send_message(first, session_id, "synthetic message")
        assert response.status_code == 200
        assert response.json()["triage"]["level"] == "needs_more_info"
        assert provider.requests  # sanity: conversation happened

    # New app instance over the same DB file == server restart.
    second_app = create_app(settings=settings)
    with TestClient(second_app) as second:
        session = second.get(f"/sessions/{session_id}")
        assert session.status_code == 200
        assert session.json()["status"] == "collecting"

        engine = build_engine(db_path)
        factory: sessionmaker[SASession] = sessionmaker(
            bind=engine, expire_on_commit=False, future=True
        )
        messages = MessageRepository(factory).list_for_session(session_id)
        assert [message.text for message in messages] == ["synthetic message"]

        # Unknown sessions still 404 after restart.
        assert second.get("/sessions/does-not-exist").status_code == 404


# ---------------------------------------------------------------------------
# Error handling, validation, and non-leakage
# ---------------------------------------------------------------------------


def test_llm_unavailable_returns_graceful_503(app_and_client) -> None:
    app, client, settings = app_and_client
    inject_orchestrator(app, settings)  # empty script queue -> LLM down
    session_id = create_session(client)
    response = send_message(client, session_id, "synthetic message")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "llm_unavailable"
    # No internal details leak to the client.
    for forbidden in ("MockProvider", "Traceback", "LLMUnavailableError"):
        assert forbidden not in response.text
    # Session stays usable (status restored, not stuck in assessing).
    assert client.get(f"/sessions/{session_id}").json()["status"] == "collecting"


def test_unknown_session_returns_404_envelope(app_and_client) -> None:
    _, client, _ = app_and_client
    response = send_message(client, "no-such-session", "synthetic message")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "session_not_found",
            "message": "Session no-such-session was not found.",
        }
    }


def test_blank_message_rejected(app_and_client) -> None:
    _, client, _ = app_and_client
    session_id = create_session(client)
    response = send_message(client, session_id, "   ")
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "message_empty"


def test_oversized_message_rejected(app_and_client) -> None:
    _, client, settings = app_and_client
    session_id = create_session(client)
    response = send_message(client, session_id, "x" * (settings.sehat_max_message_chars + 1))
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "message_too_long"


def test_malformed_body_rejected_without_echoing_input(app_and_client) -> None:
    _, client, _ = app_and_client
    session_id = create_session(client)
    response = client.post(
        f"/sessions/{session_id}/messages", json={"text": {"secret": "SYNDROME-XYZ"}}
    )
    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "validation_error"
    # Submitted content must never be echoed back.
    assert "SYNDROME-XYZ" not in response.text


def test_invalid_language_rejected(app_and_client) -> None:
    _, client, _ = app_and_client
    response = client.post("/sessions", json={"preferred_language": "xx"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_request_ids_present_on_all_conversation_endpoints(app_and_client) -> None:
    app, client, settings = app_and_client
    inject_orchestrator(app, settings, scripts=(case_json(),))
    created = client.post("/sessions", json={})
    session_id = created.json()["id"]
    sent = send_message(client, session_id, "synthetic message")
    fetched = client.get(f"/sessions/{session_id}")
    for response in (created, sent, fetched):
        request_id = response.headers.get("X-Request-ID")
        assert request_id and len(request_id) == 32
    assert len({r.headers["X-Request-ID"] for r in (created, sent, fetched)}) == 3
