"""Deterministic triage engine tests (Phase 1).

Synthetic structural fixtures only; they verify precedence, traceability,
and determinism — not medical content.
"""

from __future__ import annotations

from app.models import Condition, SafetyLevel, SymptomReport, TriageLevel
from app.safety.engine import evaluate_rules
from app.triage.engine import decide
from conftest import make_case, make_rule

EMERGENCY = make_rule("T-EMG", SafetyLevel.EMERGENCY, Condition(red_flag_signal="SIG-1"))
URGENT = make_rule("T-URG", SafetyLevel.URGENT, Condition(min_severity=5))
MONITOR = make_rule("T-MON", SafetyLevel.MONITOR, Condition(min_severity=1))


def triage_for(case, rules):
    return decide(case, evaluate_rules(rules, case))


def test_emergency_rule_wins_over_missing_information() -> None:
    case = make_case(missing_fields=["symptoms.duration"], red_flag_signals=["SIG-1"])
    decision = triage_for(case, [EMERGENCY])
    assert decision.level == TriageLevel.EMERGENCY
    assert decision.fired_rule_ids == ["T-EMG"]


def test_urgent_rule_maps_to_same_day() -> None:
    case = make_case(symptoms=[SymptomReport(name="s", severity=7)])
    decision = triage_for(case, [URGENT])
    assert decision.level == TriageLevel.URGENT_SAME_DAY
    assert decision.fired_rule_ids == ["T-URG"]


def test_monitor_rule_with_complete_case_maps_to_routine() -> None:
    case = make_case(symptoms=[SymptomReport(name="s", severity=2)])
    decision = triage_for(case, [MONITOR])
    assert decision.level == TriageLevel.ROUTINE
    assert decision.recheck_advice is not None
    assert decision.self_care_limits == []


def test_complete_case_without_flags_maps_to_self_care() -> None:
    decision = triage_for(make_case(), [])
    assert decision.level == TriageLevel.SELF_CARE
    assert decision.fired_rule_ids == []
    assert decision.self_care_limits != []
    assert decision.recheck_advice is not None


def test_missing_information_without_flags_maps_to_needs_more_info() -> None:
    case = make_case(missing_fields=["symptoms.duration"])
    decision = triage_for(case, [])
    assert decision.level == TriageLevel.NEEDS_MORE_INFO
    assert decision.recheck_advice is None


def test_monitor_flag_with_missing_information_asks_questions_first() -> None:
    case = make_case(
        symptoms=[SymptomReport(name="s", severity=2)],
        missing_fields=["demographics.age_group"],
    )
    decision = triage_for(case, [MONITOR])
    assert decision.level == TriageLevel.NEEDS_MORE_INFO


def test_conflicting_rules_highest_level_wins_all_ids_traced() -> None:
    case = make_case(
        symptoms=[SymptomReport(name="s", severity=7)],
        red_flag_signals=["SIG-1"],
    )
    decision = triage_for(case, [MONITOR, URGENT, EMERGENCY])
    assert decision.level == TriageLevel.EMERGENCY
    assert decision.fired_rule_ids == ["T-MON", "T-URG", "T-EMG"]


def test_urgent_beats_monitor() -> None:
    case = make_case(symptoms=[SymptomReport(name="s", severity=7)])
    decision = triage_for(case, [MONITOR, URGENT])
    assert decision.level == TriageLevel.URGENT_SAME_DAY


def test_every_level_carries_next_actions() -> None:
    cases_rules = [
        (make_case(red_flag_signals=["SIG-1"]), [EMERGENCY]),
        (make_case(symptoms=[SymptomReport(name="s", severity=7)]), [URGENT]),
        (make_case(symptoms=[SymptomReport(name="s", severity=2)]), [MONITOR]),
        (make_case(), []),
        (make_case(missing_fields=["x"]), []),
    ]
    levels_seen = set()
    for case, rules in cases_rules:
        decision = triage_for(case, rules)
        assert decision.next_actions, f"{decision.level} has no next actions"
        levels_seen.add(decision.level)
    assert levels_seen == set(TriageLevel)


def test_triage_is_deterministic() -> None:
    case = make_case(
        symptoms=[SymptomReport(name="s", severity=7)],
        red_flag_signals=["SIG-1"],
    )
    first = triage_for(case, [MONITOR, URGENT, EMERGENCY])
    second = triage_for(case, [MONITOR, URGENT, EMERGENCY])
    assert first.model_dump() == second.model_dump()
