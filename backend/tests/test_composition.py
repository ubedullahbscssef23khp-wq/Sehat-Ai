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
from app.conversation.responses import DISCLAIMER, NO_EVIDENCE_NOTE
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


@pytest.mark.parametrize("language, expected", [(Language.UR, "\u06d2"), (Language.SD, "\u067a")])
def test_deterministic_localized_copy_is_real_unicode(language: Language, expected: str) -> None:
    texts = [DISCLAIMER, NO_EVIDENCE_NOTE, fallback_user_message(TriageLevel.EMERGENCY)]
    localized = " ".join(text.for_language(language) for text in texts)
    assert expected in localized
    assert not any(marker in localized for marker in ("Ã", "â", "ð", "╪", "┘"))


def test_retriever_rejects_nothing_but_returns_deterministically() -> None:
    entry = make_knowledge_entry("T-KB-1", terms=("alpha",))
    retriever = LexicalKnowledgeRetriever([entry])
    case = StructuredCase.model_validate_json(case_json())
    assert retriever.retrieve(case) == retriever.retrieve(case)


# ---------------------------------------------------------------------------
# Multilingual response composition & LocalizedText field assignment
# ---------------------------------------------------------------------------


def test_english_response_places_generated_text_in_en(tmp_path: Path) -> None:
    synthetic_en = "Please monitor your symptoms and rest."
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), synthetic_en),
    )
    session = harness.orchestrator.create_session(preferred_language=Language.EN)
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    assert response.user_message.en == synthetic_en
    assert response.user_message.ur is None
    assert response.user_message.sd is None
    assert response.user_message.for_language(Language.EN) == synthetic_en
    # Verify no extra LLM call (1 for extraction, 1 for composition)
    assert isinstance(harness.provider, MockProvider)
    assert len(harness.provider.requests) == 2


def test_urdu_response_assigns_generated_text_to_ur_not_en(tmp_path: Path) -> None:
    synthetic_ur = "براہ کرم اپنی علامات کی نگرانی کریں اور آرام کریں۔"
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), synthetic_ur),
    )
    session = harness.orchestrator.create_session(preferred_language=Language.UR)
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    # generated text is assigned to LocalizedText.ur
    assert response.user_message.ur == synthetic_ur
    # it is NOT incorrectly copied into LocalizedText.en
    assert response.user_message.en != synthetic_ur
    # en retains deterministic English fallback text
    assert response.user_message.en == fallback_user_message(response.triage.level).en
    assert response.user_message.sd is None
    # for_language resolves correctly
    assert response.user_message.for_language(Language.UR) == synthetic_ur
    assert response.user_message.for_language(Language.EN) == fallback_user_message(response.triage.level).en
    # Verify no extra LLM call (1 for extraction, 1 for composition)
    assert isinstance(harness.provider, MockProvider)
    assert len(harness.provider.requests) == 2
    # API structure compatibility: disclaimers and schema intact
    assert len(response.disclaimers) >= 1
    assert response.session_id == session.id


def test_sindhi_response_assigns_generated_text_to_sd_not_en(tmp_path: Path) -> None:
    synthetic_sd = "مهرباني ڪري پنهنجي علامتن جي نگراني ڪريو ۽ آرام ڪريو."
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), synthetic_sd),
    )
    session = harness.orchestrator.create_session(preferred_language=Language.SD)
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    # generated text is assigned to LocalizedText.sd
    assert response.user_message.sd == synthetic_sd
    # it is NOT incorrectly copied into LocalizedText.en
    assert response.user_message.en != synthetic_sd
    # en retains deterministic English fallback text
    assert response.user_message.en == fallback_user_message(response.triage.level).en
    assert response.user_message.ur is None
    # for_language resolves correctly
    assert response.user_message.for_language(Language.SD) == synthetic_sd
    assert response.user_message.for_language(Language.EN) == fallback_user_message(response.triage.level).en
    # Verify no extra LLM call (1 for extraction, 1 for composition)
    assert isinstance(harness.provider, MockProvider)
    assert len(harness.provider.requests) == 2
    # API structure compatibility: disclaimers and schema intact
    assert len(response.disclaimers) >= 1
    assert response.session_id == session.id


def test_multilingual_output_policy_violation_falls_back_safely(tmp_path: Path) -> None:
    # Diagnostic claim violates policy
    violating_text = "You have malaria. Take chloroquine."
    harness = OrchestratorHarness(
        tmp_path,
        scripts=(case_json(), violating_text),
    )
    session = harness.orchestrator.create_session(preferred_language=Language.UR)
    response = asyncio.run(harness.orchestrator.handle_message(session.id, "synthetic message"))
    # Falls back to deterministic fallback with all languages
    expected_fallback = fallback_user_message(response.triage.level)
    assert response.user_message == expected_fallback
    assert response.user_message.for_language(Language.UR) == expected_fallback.ur
    assert "malaria" not in response.user_message.for_language(Language.UR).casefold()
    assert "malaria" not in response.user_message.en.casefold()

