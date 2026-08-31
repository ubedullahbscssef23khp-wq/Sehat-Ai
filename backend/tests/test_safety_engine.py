"""Deterministic safety engine tests (Phase 1).

All fixtures are synthetic and structural; they verify engine mechanics,
not medical content.
"""

from __future__ import annotations

from pathlib import Path

from app.models import (
    AgeGroup,
    BodySystem,
    Condition,
    Demographics,
    Progression,
    SafetyLevel,
    SymptomReport,
)
from app.safety import engine
from conftest import make_case, make_rule

REPO_BACKEND = Path(__file__).resolve().parents[1]


def test_red_flag_signal_condition() -> None:
    rule = make_rule("T-SIG", SafetyLevel.EMERGENCY, Condition(red_flag_signal="SIG-1"))
    hit = engine.evaluate_rules([rule], make_case(red_flag_signals=["SIG-1"]))
    miss = engine.evaluate_rules([rule], make_case(red_flag_signals=["SIG-2"]))
    assert [fired.rule_id for fired in hit.fired_rules] == ["T-SIG"]
    assert hit.highest_level == SafetyLevel.EMERGENCY
    assert miss.fired_rules == []
    assert miss.highest_level == SafetyLevel.NONE


def test_min_severity_condition() -> None:
    rule = make_rule("T-SEV", SafetyLevel.URGENT, Condition(min_severity=9))
    severe = make_case(symptoms=[SymptomReport(name="s", severity=9)])
    mild = make_case(symptoms=[SymptomReport(name="s", severity=8)])
    unknown = make_case(symptoms=[SymptomReport(name="s")])
    assert engine.evaluate_rules([rule], severe).highest_level == SafetyLevel.URGENT
    assert engine.evaluate_rules([rule], mild).fired_rules == []
    assert engine.evaluate_rules([rule], unknown).fired_rules == []


def test_progression_condition() -> None:
    rule = make_rule("T-PROG", SafetyLevel.MONITOR, Condition(progression=Progression.WORSE))
    worsening = make_case(symptoms=[SymptomReport(name="s", progression=Progression.WORSE)])
    stable = make_case(symptoms=[SymptomReport(name="s", progression=Progression.SAME)])
    assert engine.evaluate_rules([rule], worsening).fired_rules != []
    assert engine.evaluate_rules([rule], stable).fired_rules == []


def test_pregnant_condition_does_not_fire_on_unknown() -> None:
    rule = make_rule("T-PREG", SafetyLevel.URGENT, Condition(pregnant=True))
    pregnant = make_case(demographics=Demographics(pregnant=True))
    unknown = make_case(demographics=Demographics(pregnant=None))
    assert engine.evaluate_rules([rule], pregnant).fired_rules != []
    assert engine.evaluate_rules([rule], unknown).fired_rules == []


def test_age_group_condition() -> None:
    rule = make_rule(
        "T-AGE", SafetyLevel.MONITOR,
        Condition(age_group_in=[AgeGroup.INFANT, AgeGroup.OLDER_ADULT]),
    )
    infant = make_case(demographics=Demographics(age_group=AgeGroup.INFANT))
    adult = make_case(demographics=Demographics(age_group=AgeGroup.ADULT))
    assert engine.evaluate_rules([rule], infant).fired_rules != []
    assert engine.evaluate_rules([rule], adult).fired_rules == []


def test_body_system_condition() -> None:
    rule = make_rule("T-SYS", SafetyLevel.MONITOR, Condition(body_system=BodySystem.NEUROLOGICAL))
    neuro = make_case(symptoms=[SymptomReport(name="s", body_system=BodySystem.NEUROLOGICAL)])
    skin = make_case(symptoms=[SymptomReport(name="s", body_system=BodySystem.SKIN)])
    assert engine.evaluate_rules([rule], neuro).fired_rules != []
    assert engine.evaluate_rules([rule], skin).fired_rules == []


def test_all_of_requires_every_child() -> None:
    rule = make_rule(
        "T-ALL", SafetyLevel.URGENT,
        Condition(all_of=[Condition(min_severity=5), Condition(progression=Progression.WORSE)]),
    )
    both = make_case(symptoms=[SymptomReport(name="s", severity=7, progression=Progression.WORSE)])
    one = make_case(symptoms=[SymptomReport(name="s", severity=7, progression=Progression.SAME)])
    assert engine.evaluate_rules([rule], both).fired_rules != []
    assert engine.evaluate_rules([rule], one).fired_rules == []


def test_any_of_requires_one_child_and_nesting_works() -> None:
    rule = make_rule(
        "T-ANY", SafetyLevel.URGENT,
        Condition(any_of=[
            Condition(all_of=[Condition(min_severity=9), Condition(pregnant=True)]),
            Condition(red_flag_signal="SIG-9"),
        ]),
    )
    via_signal = make_case(red_flag_signals=["SIG-9"])
    via_combo = make_case(
        symptoms=[SymptomReport(name="s", severity=10)],
        demographics=Demographics(pregnant=True),
    )
    neither = make_case(symptoms=[SymptomReport(name="s", severity=10)])
    assert engine.evaluate_rules([rule], via_signal).fired_rules != []
    assert engine.evaluate_rules([rule], via_combo).fired_rules != []
    assert engine.evaluate_rules([rule], neither).fired_rules == []


def test_multiple_rules_fire_in_rule_order_with_highest_level() -> None:
    rules = [
        make_rule("T-MON", SafetyLevel.MONITOR, Condition(min_severity=1)),
        make_rule("T-EMG", SafetyLevel.EMERGENCY, Condition(red_flag_signal="SIG-1")),
        make_rule("T-URG", SafetyLevel.URGENT, Condition(min_severity=5)),
    ]
    case = make_case(
        symptoms=[SymptomReport(name="s", severity=6)],
        red_flag_signals=["SIG-1"],
    )
    assessment = engine.evaluate_rules(rules, case)
    assert [fired.rule_id for fired in assessment.fired_rules] == ["T-MON", "T-EMG", "T-URG"]
    assert assessment.highest_level == SafetyLevel.EMERGENCY


def test_no_rules_yields_none_assessment() -> None:
    assessment = engine.evaluate_rules([], make_case())
    assert assessment.fired_rules == []
    assert assessment.highest_level == SafetyLevel.NONE


def test_evaluation_is_deterministic() -> None:
    rules = [
        make_rule("T-A", SafetyLevel.URGENT, Condition(min_severity=5)),
        make_rule("T-B", SafetyLevel.MONITOR, Condition(progression=Progression.WORSE)),
    ]
    case = make_case(symptoms=[SymptomReport(name="s", severity=6, progression=Progression.WORSE)])
    first = engine.evaluate_rules(rules, case)
    second = engine.evaluate_rules(rules, case)
    assert first.model_dump() == second.model_dump()


def test_safety_core_has_no_llm_or_network_dependencies() -> None:
    forbidden = ("httpx", "fastapi", "urllib", "socket", "requests", "app.llm")
    for module_path in (
        REPO_BACKEND / "app" / "models" / "domain.py",
        REPO_BACKEND / "app" / "safety" / "engine.py",
        REPO_BACKEND / "app" / "safety" / "loader.py",
        REPO_BACKEND / "app" / "triage" / "engine.py",
    ):
        source = module_path.read_text(encoding="utf-8")
        for token in forbidden:
            assert f"import {token}" not in source, f"{module_path.name} imports {token}"
