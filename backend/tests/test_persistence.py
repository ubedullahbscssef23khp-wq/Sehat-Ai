"""Persistence repository tests (Phase 3)."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from app.models import (
    DecisionTrace,
    Language,
    Message,
    MessageRole,
    Session,
    SessionStatus,
    StructuredCase,
)
from app.persistence.database import build_engine, init_db
from app.persistence.repositories import (
    CaseRepository,
    MessageRepository,
    SessionRepository,
    TraceRepository,
)
from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

from conversation_support import case_json


@pytest.fixture()
def factory(tmp_path: Path) -> sessionmaker[SASession]:
    engine = build_engine(tmp_path / "nested" / "dir" / "test.sqlite")
    init_db(engine)
    return sessionmaker(bind=engine, expire_on_commit=False, future=True)


def make_session(session_id: str = "s1") -> Session:
    return Session(
        id=session_id,
        created_at=datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc),
        preferred_language=Language.UR,
    )


def test_build_engine_creates_parent_directories(tmp_path: Path) -> None:
    db_path = tmp_path / "deep" / "nested" / "sehat.sqlite"
    engine = build_engine(db_path)
    init_db(engine)
    assert db_path.exists()


def test_session_round_trip_preserves_fields_and_timezone(factory) -> None:
    sessions = SessionRepository(factory)
    original = make_session()
    sessions.create(original)
    fetched = sessions.get("s1")
    assert fetched is not None
    assert fetched.id == "s1"
    assert fetched.preferred_language is Language.UR
    assert fetched.status is SessionStatus.COLLECTING
    assert fetched.created_at == original.created_at
    assert fetched.created_at.tzinfo is not None


def test_session_get_missing_returns_none(factory) -> None:
    assert SessionRepository(factory).get("missing") is None


def test_session_status_transitions(factory) -> None:
    sessions = SessionRepository(factory)
    sessions.create(make_session())
    sessions.set_status("s1", SessionStatus.ASSESSING)
    assert sessions.get("s1").status is SessionStatus.ASSESSING
    sessions.set_status("s1", SessionStatus.ESCALATED)
    assert sessions.get("s1").status is SessionStatus.ESCALATED


def test_followup_round_counter(factory) -> None:
    sessions = SessionRepository(factory)
    sessions.create(make_session())
    assert sessions.followup_rounds("s1") == 0
    assert sessions.increment_followup_rounds("s1") == 1
    assert sessions.increment_followup_rounds("s1") == 2
    assert sessions.followup_rounds("s1") == 2


def test_messages_keep_insertion_order(factory) -> None:
    sessions = SessionRepository(factory)
    sessions.create(make_session())
    messages = MessageRepository(factory)
    for index in range(3):
        messages.append(
            Message(
                id=f"m{index}",
                session_id="s1",
                role=MessageRole.USER,
                text=f"message {index}",
                lang=Language.EN,
                created_at=datetime(2026, 8, 31, 12, index, tzinfo=timezone.utc),
            )
        )
    fetched = messages.list_for_session("s1")
    assert [message.text for message in fetched] == [
        "message 0",
        "message 1",
        "message 2",
    ]
    assert messages.list_for_session("other") == []


def test_latest_case_wins(factory) -> None:
    sessions = SessionRepository(factory)
    sessions.create(make_session())
    cases = CaseRepository(factory)
    assert cases.latest("s1") is None
    first = StructuredCase.model_validate_json(case_json(chief_complaint="first"))
    second = StructuredCase.model_validate_json(case_json(chief_complaint="second"))
    cases.append("s1", first)
    cases.append("s1", second)
    latest = cases.latest("s1")
    assert latest is not None
    assert latest.chief_complaint == "second"


def test_traces_round_trip_in_order(factory) -> None:
    sessions = SessionRepository(factory)
    sessions.create(make_session())
    traces = TraceRepository(factory)
    for step in ("extraction", "safety", "triage"):
        traces.append(
            "s1",
            DecisionTrace(
                step=step,
                timestamp=datetime(2026, 8, 31, 12, 0, tzinfo=timezone.utc),
                input_hash="h",
                rule_ids=[step],
            ),
        )
    fetched = traces.list_for_session("s1")
    assert [trace.step for trace in fetched] == ["extraction", "safety", "triage"]
    assert fetched[0].rule_ids == ["extraction"]
    assert fetched[0].timestamp.tzinfo is not None
