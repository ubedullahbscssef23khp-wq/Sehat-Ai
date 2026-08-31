"""Output-policy filter tests (Phase 4 acceptance: diagnostic claims and
medication advice are blocked from final user-facing text).
"""

from __future__ import annotations

import pytest

from app.conversation.output_policy import POLICY_PATTERNS, find_violations, is_compliant
from app.conversation.responses import DISCLAIMER, NO_EVIDENCE_NOTE, fallback_user_message
from app.models import TriageLevel


@pytest.mark.parametrize(
    "text",
    [
        "You have dengue fever.",
        "you have a serious infection",
        "You've got the flu.",
        "You are suffering from chronic fatigue.",
        "you suffer from anxiety",
        "The diagnosis is malaria.",
        "Based on this, you are diagnosed with typhoid.",
        "Your condition is severe.",
    ],
)
def test_diagnostic_claims_are_blocked(text: str) -> None:
    violations = find_violations(text)
    assert violations, f"expected a violation for: {text}"
    assert all(violation.startswith("diagnostic_") for violation in violations)
    assert is_compliant(text) is False


@pytest.mark.parametrize(
    "text",
    [
        "Take paracetamol 500 mg twice a day.",
        "You should take antibiotics for this.",
        "I recommend taking ibuprofen now.",
        "Give the child aspirin.",
        "Start the medication immediately.",
        "Use this syrup three times daily.",
        "Try 250 mg of amoxicillin.",
        "You must take tablets after food.",
    ],
)
def test_medication_advice_is_blocked(text: str) -> None:
    violations = find_violations(text)
    assert violations, f"expected a violation for: {text}"
    assert all(violation.startswith("medication_") for violation in violations)
    assert is_compliant(text) is False


def test_dosage_units_are_blocked_even_without_directives() -> None:
    assert "medication_dosage_units" in find_violations("The usual amount is 500mg.")


def test_drug_names_are_blocked_even_without_directives() -> None:
    assert "medication_drug_names" in find_violations("Paracetamol can help.")


def test_blocking_is_case_insensitive() -> None:
    assert find_violations("YOU HAVE X") == find_violations("you have x")


def test_clean_guidance_text_passes() -> None:
    clean_texts = [
        "These symptoms should be assessed in person today.",
        "Please answer the follow-up questions so the guidance can be completed.",
        "Seek medical care if symptoms worsen or you become concerned.",
        "Arrange a non-urgent appointment with a healthcare professional.",
    ]
    for text in clean_texts:
        assert is_compliant(text), text


def test_server_templated_guidance_copy_is_policy_clean() -> None:
    """Templated strings substitute for filtered LLM output, so they must
    pass the same filter."""
    assert is_compliant(NO_EVIDENCE_NOTE.en)
    for level in TriageLevel:
        assert is_compliant(fallback_user_message(level).en)


def test_disclaimer_is_present_and_curated() -> None:
    """The disclaimer is fixed, human-curated server copy (not model output);
    it intentionally negates diagnosis in its wording."""
    assert DISCLAIMER.en
    assert "not" in DISCLAIMER.en and "healthcare professional" in DISCLAIMER.en


def test_policy_ids_are_stable_and_unique() -> None:
    ids = [policy_id for policy_id, _ in POLICY_PATTERNS]
    assert len(ids) == len(set(ids))
    assert "diagnostic_you_have" in ids
    assert "medication_action_take" in ids
