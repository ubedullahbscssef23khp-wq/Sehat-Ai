"""Response composition tests (Phase 4): LLM phrasing behind the output-policy
filter, deterministic fallbacks, evidence citations, and mandatory disclaimers.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.conversation.composition import MAX_COMPOSED_CHARS, ResponseComposer
from app.conversation.followups import FollowUpPhraser
from app.conversation.responses import fallback_user_message
from app.knowledge.paths import CONTENT_DIR
from app.knowledge.retrieval import LexicalKnowledgeRetriever
from app.llm.mock import MockProvider
from app.llm.trace import TraceCollector
from app.models import (
    GuidanceResponse,
    Language,
    LocalizedText,
    StructuredCase,
    TriageDecision,
    TriageLevel,
)

from conversation_support import (
    OrchestratorHarness,
    case_json,
    make_knowledge_entry,
)


def make_decision(level: TriageLevel = TriageLevel.SELF_CARE) -> TriageDecision:
    return TriageDecision(
        level=level,
        next_actions=[LocalizedText(en="synthetic next action")],
    )


def compose(provider: MockProvider) -> tuple[str, bool, list[str]]:
    composer = ResponseComposer(provider)
    collector = TraceCollector(step="response_composition")
    return asyncio.run(
        composer.compose(
            decision=make_decision(), evidence=[], language=Language.EN, collector=collector
        )
    )


# ---------------------------------------------------------------------------
# Composer unit behavior
# ---------------------------------------------------------------------------


def test_composer_uses_clean_model_text() -> None:
    provider = MockProvider(scripts=["Thanks for sharing. Please arrange a routine review."])
    text, used_fallback, violations = compose(provider)
    assert used_fallback is False
    assert violations == []
    assert text == "Thanks for sharing. Please arrange a routine review."


def test_composer_blocks_diagnostic_claim_and_falls_back() -> None:
    provider = MockProvider(scripts=["You have viral fever. Rest well."])
    text, used_fallback, violations = compose(provider)
    assert used_fallback is True
    assert "diagnostic_you_have" in violations
    assert text == fallback_user_message(TriageLevel.SELF_CARE).en
    assert "you have" not in text.casefold()


def test_composer_blocks_medication_advice_and_falls_back() -> None:
    provider = MockProvider(scripts=["Take ibuprofen 400 mg after food."])
    text, used_fallback, violations = compose(provider)
    assert used_fallback is True
    assert any(violation.startswith("medication_") for violation in violations)
    assert "ibuprofen" not in text.casefold()


def test_composer_falls_back_when_llm_unavailable() -> None:
    text, used_fallback, violations = compose(MockProvider())
    assert used_fallback is True
    assert violations == []
    assert text == fallback_user_message(TriageLevel.SELF_CARE).en


def test_composer_rejects_empty_output() -> None:
    _, used_fallback, _ = compose(MockProvider(scripts=["   "]))
    assert used_fallback is True


def test_composer_rejects_oversized_output() -> None:
    _, used_fallback, _ = compose(MockProvider(scripts=["word " * MAX_COMPOSED_CHARS]))
    assert used_fallback is True


def test_composer_strips_code_fences() -> None:
    text, used_fallback, _ = compose(MockProvider(scripts=["```\nClean message here.\n```"]))
    assert used_fallback is False
    assert text == "Clean message here."


def test_composer_records_trace_with_template_id() -> None:
    provider = MockProvider(scripts=["You have X."])
    composer = ResponseComposer(provider)
    collector = TraceCollector(step="response_composition")
    asyncio.run(
        composer.compose(decision=make_decision(), evidence=[], language=Language.EN, collector=collector)
    )
    trace = collector.finalize({})
    assert trace.llm_calls[0].template_id == "compose.v1"
    assert trace.llm_calls[0].valid is False


def test_compose_prompt_is_constrained_to_provided_facts() -> None:
    provider = MockProvider(scripts=["Clean message."])
    compose(provider)
    user_prompt = provider.requests[0].messages[-1].content
    assert "synthetic next action" in user_prompt
    assert "self_care" in user_prompt
    assert "(none available)" in user_prompt


# ---------------------------------------------------------------------------
# Follow-up phrasing is policy-filtered too
# ---------------------------------------------------------------------------


def test_phraser_rejects_policy_violating_questions() -> None:
    phraser = FollowUpPhraser(MockProvider(scripts=['["Do you have diabetes?"]']))
    collector = TraceCollector(step="followup_phrasing")
    questions, used_fallback = asyncio.run(
        phraser.phrase(["demographics.age_group"], Language.EN, collector)
    )
    assert used_fallback is True
    assert all("you have" not in question.en.casefold() for question in questions)


# ---------------------------------------------------------------------------
# Orchestrator-level evidence behavior (acceptance: citations vs honest note)
# ---------------------------------------------------------------------------


def test_final_response_includes_citation_when_knowledge_matches(tmp_path: Path) -> None:
    entry = make_knowledge_entry("T-KB-1", terms=("synthetic-symptom", "synthetic"))
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), "Thanks for sharing. Please arrange a routine review."),
        knowledge=[entry],
    )
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert len(response.evidence) == 1
    citation = response.evidence[0]
    assert citation.source == entry.source
    assert citation.date_reviewed == entry.date_reviewed
    assert citation.snippet == entry.content
    assert response.evidence_note is None
    assert response.user_message.en == "Thanks for sharing. Please arrange a routine review."


def test_final_response_shows_honest_note_when_no_knowledge_matches(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.evidence == []
    assert response.evidence_note is not None
    assert "No reliable information" in response.evidence_note.en
    # Composition fell back deterministically (empty mock queue).
    assert response.user_message == fallback_user_message(TriageLevel.SELF_CARE)


def test_policy_violating_composition_never_reaches_user(tmp_path: Path) -> None:
    harness = OrchestratorHarness(
        tmp_path, scripts=(case_json(), "You have malaria. Take chloroquine.")
    )
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.user_message == fallback_user_message(TriageLevel.SELF_CARE)
    assert "malaria" not in response.user_message.en.casefold()
    assert response.triage.level is TriageLevel.SELF_CARE


def test_shipped_corpus_yields_only_honest_notes(tmp_path: Path) -> None:
    """With the (empty) shipped corpus, every final response carries the
    honest note and never fabricated evidence."""
    from app.knowledge.loader import load_entries_dir

    entries = load_entries_dir(CONTENT_DIR)
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),), knowledge=entries)
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.evidence == []
    assert response.evidence_note is not None


# ---------------------------------------------------------------------------
# Mandatory disclaimer enforcement (acceptance: server-side validation)
# ---------------------------------------------------------------------------


def test_guidance_response_without_disclaimers_fails_validation() -> None:
    with pytest.raises(ValidationError):
        GuidanceResponse(
            session_id="s1",
            user_message=LocalizedText(en="message"),
            triage=make_decision(),
            disclaimers=[],
        )


def test_every_api_like_response_carries_disclaimers(tmp_path: Path) -> None:
    harness = OrchestratorHarness(tmp_path, scripts=(case_json(),))
    session = harness.orchestrator.create_session()
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert len(response.disclaimers) >= 1
    assert "not" in response.disclaimers[0].en


def test_retriever_rejects_nothing_but_returns_deterministically() -> None:
    entry = make_knowledge_entry("T-KB-1", terms=("alpha",))
    retriever = LexicalKnowledgeRetriever([entry])
    case = StructuredCase.model_validate_json(case_json())
    assert retriever.retrieve(case) == retriever.retrieve(case)
