"""Domain model validation tests (Phase 1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models import (
    AgeGroup,
    BodySystem,
    Condition,
    Language,
    LocalizedText,
    Progression,
    RedFlagRule,
    SafetyLevel,
    StructuredCase,
    SymptomReport,
    TriageLevel,
)
from conftest import make_case


def test_structured_case_defaults() -> None:
    case = make_case()
    assert case.symptoms == []
    assert case.demographics.age_group is None
    assert case.demographics.pregnant is None
    assert case.missing_fields == []
    assert case.red_flag_signals == []
    assert case.confidence == 0.0


def test_structured_case_requires_chief_complaint() -> None:
    with pytest.raises(ValidationError):
        StructuredCase(chief_complaint="")


def test_severity_bounds_enforced() -> None:
    with pytest.raises(ValidationError):
        SymptomReport(name="s", severity=11)
    with pytest.raises(ValidationError):
        SymptomReport(name="s", severity=-1)
    assert SymptomReport(name="s", severity=10).severity == 10
    assert SymptomReport(name="s").severity is None


def test_confidence_bounds_enforced() -> None:
    with pytest.raises(ValidationError):
        make_case(confidence=1.5)
    with pytest.raises(ValidationError):
        make_case(confidence=-0.1)


def test_localized_text_falls_back_to_english() -> None:
    text = LocalizedText(en="hello", ur="سلام")
    assert text.for_language(Language.EN) == "hello"
    assert text.for_language(Language.UR) == "سلام"
    assert text.for_language(Language.SD) == "hello"


def test_level_enums_match_architecture() -> None:
    assert {level.value for level in SafetyLevel} == {"none", "monitor", "urgent", "emergency"}
    assert {level.value for level in TriageLevel} == {
        "emergency",
        "urgent_same_day",
        "routine",
        "self_care",
        "needs_more_info",
    }


def test_condition_requires_exactly_one_kind() -> None:
    with pytest.raises(ValidationError):
        Condition()
    with pytest.raises(ValidationError):
        Condition(min_severity=5, pregnant=True)


def test_condition_combinators_must_not_be_empty() -> None:
    with pytest.raises(ValidationError):
        Condition(all_of=[])
    with pytest.raises(ValidationError):
        Condition(any_of=[])


def test_condition_allows_nested_combinators() -> None:
    condition = Condition(
        all_of=[
            Condition(any_of=[Condition(min_severity=5), Condition(pregnant=True)]),
            Condition(progression=Progression.WORSE),
        ]
    )
    assert condition.all_of is not None and len(condition.all_of) == 2


def test_red_flag_rule_requires_provenance() -> None:
    with pytest.raises(ValidationError):
        RedFlagRule(
            id="R-1", description="d", level=SafetyLevel.URGENT,
            when=Condition(min_severity=5), review_date="2026-01-01",
        )
    with pytest.raises(ValidationError):
        RedFlagRule(
            id="R-1", description="d", level=SafetyLevel.URGENT,
            when=Condition(min_severity=5), source="src",
        )


def test_red_flag_rule_rejects_level_none() -> None:
    with pytest.raises(ValidationError):
        RedFlagRule(
            id="R-1", description="d", level=SafetyLevel.NONE,
            when=Condition(min_severity=5), source="src", review_date="2026-01-01",
        )


def test_symptom_report_fields() -> None:
    symptom = SymptomReport(
        name="headache", body_system=BodySystem.NEUROLOGICAL,
        severity=4, progression=Progression.SAME, duration="2 days",
    )
    assert symptom.body_system == BodySystem.NEUROLOGICAL
    assert AgeGroup.OLDER_ADULT.value == "older_adult"


def test_localized_text_is_immutable() -> None:
    text = LocalizedText(en="hello", ur="سلام")
    with pytest.raises(ValidationError):
        text.en = "changed"
    with pytest.raises(ValidationError):
        text.ur = None
    assert text.en == "hello"
    assert text.ur == "سلام"


def test_condition_rejects_empty_red_flag_signal() -> None:
    with pytest.raises(ValidationError):
        Condition(red_flag_signal="")


def test_condition_rejects_empty_age_group_in() -> None:
    with pytest.raises(ValidationError):
        Condition(age_group_in=[])
