"""Conversation orchestration tests (Phase 3).

Fixtures are synthetic and structural; they exercise the state machine and
safety invariants, not medical content.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from pathlib import Path

import pytest

from app.conversation.completeness import missing_required_fields
from app.conversation.errors import SessionClosedError, SessionNotFoundError
from app.conversation.followups import FollowUpPhraser
from app.conversation.orchestrator import ConversationOrchestrator
from app.llm.mock import MockProvider
from app.llm.provider import LLMUnavailableError
from app.llm.trace import TraceCollector
from app.llm.types import LLMRequest, LLMResponse
from app.models import (
    Language,
    SafetyLevel,
    SessionStatus,
    StructuredCase,
    TriageLevel,
)
from app.persistence.repositories import SessionRepository, TraceRepository

from conversation_support import (
    OrchestratorHarness,
    case_json,
    incomplete_case_json,
    make_pattern,
    make_signal_rule,
    questions_json,
)


# ---------------------------------------------------------------------------
# Deterministic completeness
# ---------------------------------------------------------------------------


def test_completeness_reports_all_missing_fields() -> None:
    case = StructuredCase(chief_complaint="synthetic")
    assert missing_required_fields(case) == [
        "symptoms",
        "demographics.age_group",
        "demographics.pregnant",
    ]


def test_completeness_empty_when_case_is_complete() -> None:
    case = StructuredCase.model_validate_json(case_json())
    assert missing_required_fields(case) == []


def test_completeness_reports_only_age_group() -> None:
    case = StructuredCase.model_validate_json(incomplete_case_json())
    assert missing_required_fields(case) == ["demographics.age_group"]


# ---------------------------------------------------------------------------
# Follow-up phrasing: LLM phrases only, deterministic fallback always exists
# ---------------------------------------------------------------------------


def test_phraser_falls_back_when_llm_unavailable() -> None:
    phraser = FollowUpPhraser(MockProvider())
    collector = TraceCollector(step="followup_phrasing")
    questions, used_fallback = asyncio.run(
        phraser.phrase(["demographics.age_group"], Language.EN, collector)
    )
    assert used_fallback is True
    assert len(questions) == 1
    assert "age group" in questions[0].en
    assert collector.calls[0].valid is False


def test_phraser_falls_back_on_invalid_model_output() -> None:
    phraser = FollowUpPhraser(MockProvider(scripts=["not a json array"]))
    collector = TraceCollector(step="followup_phrasing")
    questions, used_fallback = asyncio.run(
        phraser.phrase(["symptoms", "demographics.pregnant"], Language.EN, collector)
    )
    assert used_fallback is True
    assert len(questions) == 2


def test_phraser_uses_model_questions_when_valid() -> None:
    phraser = FollowUpPhraser(MockProvider(scripts=[questions_json(1)]))
    collector = TraceCollector(step="followup_phrasing")
    questions, used_fallback = asyncio.run(
        phraser.phrase(["demographics.age_group"], Language.EN, collector)
    )
    assert used_fallback is False
    assert questions[0].en == "synthetic question 1?"
    assert collector.calls[0].valid is True


# ---------------------------------------------------------------------------
# Orchestrator state machine
# ---------------------------------------------------------------------------


def test_create_and_get_session(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path)
    session = harness.orchestrator.create_session(Language.UR)
    assert session.status is SessionStatus.COLLECTING
    fetched = harness.orchestrator.get_session(session.id)
    assert fetched is not None
    assert fetched.preferred_language is Language.UR


def test_handle_message_unknown_session_raises(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path)
    with pytest.raises(SessionNotFoundError):
        asyncio.run(harness.orchestrator.handle_message("missing", "hello"))


def test_handle_message_closed_session_raises(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path)
    session = harness.orchestrator.create_session()
    SessionRepository(harness.session_factory).set_status(session.id, SessionStatus.CLOSED)
    with pytest.raises(SessionClosedError):
        asyncio.run(harness.orchestrator.handle_message(session.id, "hello"))


def test_prescreen_short_circuits_without_any_llm_call(tmp_path: Path) -> None:
    """Acceptance (d): the emergency pre-screen is deterministic and runs
    before any LLM work — it works even with the LLM completely down."""
    harness = OrchestratorHarness(tmp_path, patterns=[make_pattern()])
    session = harness.orchestrator.create_session()
    response = asyncio.run(
        harness.orchestrator.handle_message(
            session.id, "I have SYNTHETIC-CHEST-PAIN right now"
        )
    )
    assert response.triage.level is TriageLevel.EMERGENCY
    assert response.triage.fired_rule_ids == ["T-PRESCREEN-1"]
    assert response.follow_up_questions == []
    assert len(response.disclaimers) >= 1
    assert harness.provider.requests == []  # zero LLM calls
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.ESCALATED
    traces = TraceRepository(harness.session_factory).list_for_session(session.id)
    assert [trace.step for trace in traces] == ["prescreen"]


def test_two_invalid_extractions_yield_rephrase_guidance(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path, scripts=("not json", "still not json"))
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "blurry message"))
    assert response.triage.level is TriageLevel.NEEDS_MORE_INFO
    assert "could not fully understand" in response.user_message.en
    assert len(harness.provider.requests) == 2  # exactly one retry
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.COLLECTING


def test_llm_unavailable_restores_session_status_and_raises(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path)  # empty queue -> LLMUnavailableError
    session = harness.orchestrator.create_session()
    with pytest.raises(LLMUnavailableError):
        asyncio.run(harness.orchestrator.handle_message(session.id, "I have a cough"))
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.COLLECTING


def test_model_claimed_missing_fields_are_replaced_by_deterministic_check(tmp_path: Path) -> None:
    """The LLM's own gap report is never trusted: a complete case claiming
    gaps is not asked about them, and the stored case carries the
    deterministic list."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(missing_fields=["chief_complaint"]),))
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.triage.level is TriageLevel.SELF_CARE
    assert response.follow_up_questions == []
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.GUIDED


def test_safety_flags_take_precedence_over_missing_info(tmp_path: Path) -> None:
    """An urgent rule must never be delayed by follow-up questions."""
    rule = make_signal_rule("T-RULE-1", "synthetic_flag", SafetyLevel.URGENT)
    payload_dict = json.loads(incomplete_case_json())
    payload_dict["red_flag_signals"] = ["synthetic_flag"]
    harness = OrchestratorHarness(tmp_path, scripts=(json.dumps(payload_dict),), rules=[rule])
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.triage.level is TriageLevel.URGENT_SAME_DAY
    assert response.follow_up_questions == []
    # Extraction + composition only: no follow-up phrasing call happened.
    assert len(harness.provider.requests) == 2
    assert all("Topics:" not in request.messages[-1].content for request in harness.provider.requests)
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.ESCALATED


def test_followup_rounds_capped_then_best_effort_with_limited_confidence(tmp_path: Path) -> None:
    """Acceptance (b): at most 2 follow-up rounds, then best-effort triage
    marked limited-confidence."""
    scripts = (
        incomplete_case_json(),
        "not json",  # phrasing falls back deterministically
        incomplete_case_json(),
        "not json",
        incomplete_case_json(),
    )
    harness = OrchestratorHarness(tmp_path, scripts=scripts)
    session = harness.orchestrator.create_session()

    first = asyncio.run(harness.orchestrator.handle_message(session.id, "message one"))
    assert first.triage.level is TriageLevel.NEEDS_MORE_INFO
    assert len(first.follow_up_questions) == 1
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.COLLECTING

    second = asyncio.run(harness.orchestrator.handle_message(session.id, "message two"))
    assert second.triage.level is TriageLevel.NEEDS_MORE_INFO
    assert len(second.follow_up_questions) == 1

    third = asyncio.run(harness.orchestrator.handle_message(session.id, "message three"))
    assert third.follow_up_questions == []
    assert third.triage.level is not TriageLevel.NEEDS_MORE_INFO
    assert third.triage.limited_confidence is True
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.GUIDED


def test_followups_ask_only_computed_missing_fields(tmp_path: Path) -> None:
    """Age group missing only -> exactly one question; the phrasing request
    must mention the computed field and nothing else."""
    harness = OrchestratorHarness(
        tmp_path, scripts=(incomplete_case_json(), questions_json(1))
    )
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert len(response.follow_up_questions) == 1
    phrasing_request = harness.provider.requests[-1]
    user_text = phrasing_request.messages[-1].content
    assert "demographics.age_group" in user_text
    assert "demographics.pregnant" not in user_text
    assert "symptoms" not in user_text


def test_traces_recorded_with_consistent_input_hash(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session()
    text = "synthetic message"
    asyncio.run(harness.orchestrator.handle_message(session.id, text))
    traces = TraceRepository(harness.session_factory).list_for_session(session.id)
    assert [trace.step for trace in traces] == [
        "extraction",
        "safety",
        "triage",
        "knowledge_retrieval",
        "response_composition",
    ]
    expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert all(trace.input_hash == expected_hash for trace in traces)
    extraction_trace = traces[0]
    assert extraction_trace.llm_calls[0].template_id == "extraction.v2"
    triage_trace = traces[2]
    assert triage_trace.outputs["level"] == "self_care"
    assert triage_trace.outputs["limited_confidence"] is False
    retrieval_trace = traces[3]
    assert retrieval_trace.outputs["entry_ids"] == []
    composition_trace = traces[4]
    assert composition_trace.outputs["fallback_used"] is True


def test_decision_traces_do_not_store_raw_user_text(tmp_path: Path) -> None:
    raw_text = "private synthetic health text"
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session()
    asyncio.run(harness.orchestrator.handle_message(session.id, raw_text))

    traces = TraceRepository(harness.session_factory).list_for_session(session.id)
    serialized = json.dumps([trace.model_dump(mode="json") for trace in traces])
    assert raw_text not in serialized
    assert hashlib.sha256(raw_text.encode("utf-8")).hexdigest() in serialized


def test_provider_is_swappable_behind_protocol(tmp_path: Path) -> None:
    """Any object satisfying the LLMProvider protocol can drive the flow."""

    class ScriptedProvider:
        model_name = "custom-scripted"

        async def complete(self, request: LLMRequest) -> LLMResponse:
            return LLMResponse(model=self.model_name, text=case_json())

    harness = OrchestratorHarness(tmp_path, provider=ScriptedProvider())
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.triage.level is TriageLevel.SELF_CARE
    assert harness.orchestrator.get_session(session.id).status is SessionStatus.GUIDED


def test_safety_path_is_independent_of_llm_when_rules_fire(tmp_path: Path) -> None:
    """Prescreen + rule evaluation are pure Python: with the LLM unavailable,
    an emergency pattern still escalates."""
    harness = OrchestratorHarness(tmp_path, patterns=[make_pattern()])  # empty LLM queue
    session = harness.orchestrator.create_session()
    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "synthetic-chest-pain")
    )
    assert response.triage.level is TriageLevel.EMERGENCY
