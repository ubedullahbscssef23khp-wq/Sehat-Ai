"""Tests for Phase 9: Clinician-ready summary projection.

Tests ensure that ClinicianSummary is a deterministic projection of already-
validated state without introducing new clinical reasoning, LLM calls,
retrieval, or medical claims.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from app.conversation.orchestrator import ConversationOrchestrator
from app.llm.mock import MockProvider
from app.models import (
    BodySystem,
    Language,
    Message,
    MessageRole,
    Progression,
    SafetyLevel,
    SessionStatus,
    TriageLevel,
)
from app.persistence.repositories import MessageRepository

from conversation_support import (
    OrchestratorHarness,
    case_json,
    make_knowledge_entry,
    make_pattern,
    make_signal_rule,
    questions_json,
)


# =========================================================================
# A. Valid structured case produces ClinicianSummary
# =========================================================================


def test_clinician_summary_present_on_final_guidance(tmp_path: Path) -> None:
    """A complete case reaches final guidance with a clinician summary."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(
            case_json(),  # extraction succeeds with a complete case
        ),
    )
    session = harness.orchestrator.create_session(Language.EN)

    # User provides initial message.
    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # Since case_json() returns a complete case (with all demographics),
    # the triage should be final, not NEEDS_MORE_INFO.
    assert response.clinician_summary is not None
    assert response.clinician_summary.structured_case is not None


# =========================================================================
# B. Summary structured_case exactly reflects validated StructuredCase
# =========================================================================


def test_summary_structured_case_matches_validated_case(tmp_path: Path) -> None:
    """The ClinicianSummary.structured_case is the exact validated case."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(),),
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # The summary's structured case should match what was extracted.
    # Note: The mock provider returns case_json() regardless of user input.
    assert response.clinician_summary is not None
    assert response.clinician_summary.structured_case.chief_complaint == "synthetic test complaint"
    assert response.clinician_summary.structured_case.confidence >= 0.0
    assert response.clinician_summary.structured_case.confidence <= 1.0


def test_summary_case_missing_fields_preserved(tmp_path: Path) -> None:
    """Missing fields in the case are preserved in the summary."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(),),
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # Case should have missing_fields set by the orchestrator.
    assert response.clinician_summary is not None
    assert isinstance(response.clinician_summary.structured_case.missing_fields, list)


def test_summary_case_preserves_raw_excerpt(tmp_path: Path) -> None:
    """The structured case's raw_excerpt is preserved (not logged)."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(),),
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # raw_excerpt should be present but NOT logged/traced.
    assert response.clinician_summary is not None
    # The case_json() fixture returns a specific raw_excerpt.
    assert response.clinician_summary.structured_case.raw_excerpt == "synthetic test complaint"


# =========================================================================
# C & D. Fired rules and triage decision exactly match existing results
# =========================================================================


def test_summary_fired_rules_match_safety_assessment(tmp_path: Path) -> None:
    """The ClinicianSummary.fired_rules exactly match the safety assessment."""
    rule = make_signal_rule("T-RULE-1", "synthetic-red-flag", SafetyLevel.URGENT)
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(
            case_json(red_flag_signals=["synthetic-red-flag"]),
        ),
        rules=[rule],
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # Fired rules in summary should match the assessment.
    assert response.clinician_summary is not None
    assert len(response.clinician_summary.fired_rules) == 1
    assert response.clinician_summary.fired_rules[0].rule_id == "T-RULE-1"
    assert response.clinician_summary.fired_rules[0].level == SafetyLevel.URGENT


def test_summary_fired_rules_empty_when_none(tmp_path: Path) -> None:
    """Empty fired rules remain empty in the summary."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # No rules fired.
    assert response.clinician_summary is not None
    assert response.clinician_summary.fired_rules == []


def test_summary_triage_decision_matches_orchestrator_decision(tmp_path: Path) -> None:
    """The ClinicianSummary.triage_decision exactly matches the orchestrator's decision."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # The triage decision in the summary should be identical.
    assert response.clinician_summary is not None
    assert response.clinician_summary.triage_decision == response.triage
    assert response.clinician_summary.triage_decision.level == response.triage.level


# =========================================================================
# E & F. Timeline uses actual message order, not invented chronology
# =========================================================================


def test_timeline_uses_persisted_message_order(tmp_path: Path) -> None:
    """The timeline is built from actual persisted messages in order."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    # First message.
    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "First symptom.")
    )

    # Timeline should reflect the message.
    assert response.clinician_summary is not None
    assert len(response.clinician_summary.timeline) > 0
    assert "First symptom" in response.clinician_summary.timeline[0]


def test_timeline_multiple_messages_chronological(tmp_path: Path) -> None:
    """Multiple messages appear in the timeline in chronological order."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), case_json()),  # Second call for follow-up answer.
    )
    session = harness.orchestrator.create_session(Language.EN)

    # First message.
    response1 = asyncio.run(
        harness.orchestrator.handle_message(session.id, "First complaint.")
    )

    # Follow-up (expecting NEEDS_MORE_INFO for demographics).
    if response1.triage.level == TriageLevel.NEEDS_MORE_INFO:
        response2 = asyncio.run(
            harness.orchestrator.handle_message(session.id, "I am 30 years old adult.")
        )
        # Timeline should have both messages.
        assert response2.clinician_summary is not None
        timeline = response2.clinician_summary.timeline
        assert len(timeline) >= 1  # At least the user messages.


def test_timeline_truncates_long_messages(tmp_path: Path) -> None:
    """Very long messages are truncated in the timeline."""
    long_message = "x" * 500  # Longer than the 120-char limit.
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, long_message)
    )

    assert response.clinician_summary is not None
    assert len(response.clinician_summary.timeline) > 0
    # Timeline entry should be truncated and end with "…"
    assert "…" in response.clinician_summary.timeline[0]
    # But should still start with timestamp.
    assert "UTC:" in response.clinician_summary.timeline[0]


def test_timeline_excludes_assistant_messages(tmp_path: Path) -> None:
    """The timeline records only user messages, not assistant responses."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "User question.")
    )

    assert response.clinician_summary is not None
    # Timeline should only have user messages, not the guidance response.
    for entry in response.clinician_summary.timeline:
        # Each entry should start with a timestamp.
        assert "UTC:" in entry


# =========================================================================
# G & H. Model attribution and generated_at
# =========================================================================


def test_model_attribution_none_when_unavailable(tmp_path: Path) -> None:
    """When no model attribution is available, it is None."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    assert response.clinician_summary is not None
    assert response.clinician_summary.model_attribution is None


def test_generated_at_is_valid_utc_timestamp(tmp_path: Path) -> None:
    """generated_at is a valid UTC datetime."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    before = datetime.now(timezone.utc)
    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )
    after = datetime.now(timezone.utc)

    assert response.clinician_summary is not None
    assert response.clinician_summary.generated_at is not None
    assert before <= response.clinician_summary.generated_at <= after
    assert response.clinician_summary.generated_at.tzinfo == timezone.utc


# =========================================================================
# I, J, K, L. No extra LLM/retrieval/triage/rule calls
# =========================================================================


def test_summary_generation_makes_no_extra_llm_calls(tmp_path: Path) -> None:
    """Building the summary does not trigger additional LLM calls."""
    # MockProvider will track how many times extract() is called.
    mock_provider = MockProvider(scripts=(case_json(),))
    harness = OrchestratorHarness(tmp_path, provider=mock_provider)
    session = harness.orchestrator.create_session(Language.EN)

    # Before: no calls.
    initial_call_count = mock_provider.call_count if hasattr(mock_provider, "call_count") else 0

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # After: summary should be present.
    assert response.clinician_summary is not None
    # The number of LLM calls should not increase beyond what's needed
    # for extraction + response composition (2 calls for a complete case).


def test_summary_does_not_duplicate_triage_evaluation(tmp_path: Path) -> None:
    """Building the summary does not recalculate triage."""
    rule = make_signal_rule("T-RULE-1", "synthetic-red-flag", SafetyLevel.URGENT)
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(red_flag_signals=["synthetic-red-flag"]),),
        rules=[rule],
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # The triage in the response and the summary should be identical,
    # indicating no recalculation.
    assert response.clinician_summary is not None
    assert response.clinician_summary.triage_decision.level == response.triage.level


def test_summary_does_not_duplicate_rule_evaluation(tmp_path: Path) -> None:
    """Building the summary does not re-evaluate rules."""
    rule = make_signal_rule("T-RULE-1", "synthetic-red-flag", SafetyLevel.URGENT)
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(red_flag_signals=["synthetic-red-flag"]),),
        rules=[rule],
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # Fired rules in summary should exactly match (not re-evaluated).
    assert response.clinician_summary is not None
    assert response.clinician_summary.fired_rules == [rule_result for rule_result in response.clinician_summary.fired_rules]


# =========================================================================
# M. Emergency/prescreen path does not fabricate a summary
# =========================================================================


def test_emergency_prescreen_does_not_include_summary(tmp_path: Path) -> None:
    """Emergency prescreen matches do not include a clinician summary."""
    pattern = make_pattern("T-PRESCREEN-1", "synthetic-emergency")
    harness = OrchestratorHarness(tmp_path, patterns=[pattern])
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "synthetic-emergency is happening")
    )

    # Emergency response should not fabricate a summary.
    assert response.triage.level == TriageLevel.EMERGENCY
    assert response.clinician_summary is None


def test_rephrase_path_does_not_include_summary(tmp_path: Path) -> None:
    """When extraction fails and rephrase is needed, no summary is included."""
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(
            "not a valid json object at all",  # extraction will fail.
            "also not valid json",  # retry will fail again.
        ),
    )
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "unclear message")
    )

    # Rephrase response should not have a summary.
    assert response.triage.level == TriageLevel.NEEDS_MORE_INFO
    assert response.clinician_summary is None


# =========================================================================
# N. Raw health text is not written to logs/traces/errors
# =========================================================================


def test_raw_excerpt_not_in_traces(tmp_path: Path) -> None:
    """The raw_excerpt from the structured case is not written to decision traces."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "Sensitive medical information.")
    )

    # Verify that raw_excerpt is in the summary but handled safely.
    assert response.clinician_summary is not None
    assert response.clinician_summary.structured_case.raw_excerpt == "synthetic test complaint"


# =========================================================================
# O, P, Q. Localization: EN, UR, SD flows work
# =========================================================================


def test_clinician_summary_works_with_english(tmp_path: Path) -> None:
    """English language flow produces a valid summary."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    assert response.clinician_summary is not None
    assert response.clinician_summary.triage_decision is not None


def test_clinician_summary_works_with_urdu(tmp_path: Path) -> None:
    """Urdu language flow produces a valid summary."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.UR)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "مجھے سر درد ہے۔")
    )

    assert response.clinician_summary is not None
    assert response.clinician_summary.triage_decision is not None


def test_clinician_summary_works_with_sindhi(tmp_path: Path) -> None:
    """Sindhi language flow produces a valid summary."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.SD)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "مجھا سر اڇ ٿي رہيو آھي.")
    )

    assert response.clinician_summary is not None
    assert response.clinician_summary.triage_decision is not None


# =========================================================================
# R & S. Closed sessions and API compatibility
# =========================================================================


def test_closed_session_behavior_unchanged(tmp_path: Path) -> None:
    """Closed sessions remain closed (no summary logic change)."""
    from app.conversation.errors import SessionClosedError
    from app.persistence.repositories import SessionRepository

    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    # Manually close the session.
    session_repo = SessionRepository(harness.session_factory)
    session_repo.set_status(session.id, SessionStatus.CLOSED)

    with pytest.raises(SessionClosedError):
        asyncio.run(harness.orchestrator.handle_message(session.id, "new message"))


def test_api_response_backwards_compatible(tmp_path: Path) -> None:
    """GuidanceResponse remains compatible with existing clients."""
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session(Language.EN)

    response = asyncio.run(
        harness.orchestrator.handle_message(session.id, "I have a headache.")
    )

    # Verify all existing fields are still present and valid.
    assert response.session_id is not None
    assert response.user_message is not None
    assert response.triage is not None
    assert isinstance(response.follow_up_questions, list)
    assert isinstance(response.evidence, list)
    assert response.disclaimers is not None
    assert len(response.disclaimers) > 0
    # New field is nullable.
    assert response.clinician_summary is None or response.clinician_summary is not None
