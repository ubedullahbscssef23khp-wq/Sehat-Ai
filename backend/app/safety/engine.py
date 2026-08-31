"""Deterministic red-flag evaluation (ARCHITECTURE.md §8).

Pure functions over validated domain models: no I/O, no network, no LLM.
The same input always yields the same assessment, and every fired rule is
reported by stable ID so decisions are traceable.
"""

from __future__ import annotations

from app.models import (
    Condition,
    FiredRule,
    RedFlagRule,
    SafetyAssessment,
    SafetyLevel,
    StructuredCase,
)

_LEVEL_RANK: dict[SafetyLevel, int] = {
    SafetyLevel.NONE: 0,
    SafetyLevel.MONITOR: 1,
    SafetyLevel.URGENT: 2,
    SafetyLevel.EMERGENCY: 3,
}


def evaluate_condition(condition: Condition, case: StructuredCase) -> bool:
    if condition.all_of is not None:
        return all(evaluate_condition(child, case) for child in condition.all_of)
    if condition.any_of is not None:
        return any(evaluate_condition(child, case) for child in condition.any_of)
    if condition.red_flag_signal is not None:
        return condition.red_flag_signal in case.red_flag_signals
    if condition.min_severity is not None:
        return any(
            symptom.severity is not None and symptom.severity >= condition.min_severity
            for symptom in case.symptoms
        )
    if condition.progression is not None:
        return any(symptom.progression == condition.progression for symptom in case.symptoms)
    if condition.pregnant is not None:
        return case.demographics.pregnant == condition.pregnant
    if condition.age_group_in is not None:
        return case.demographics.age_group in condition.age_group_in
    if condition.body_system is not None:
        return any(symptom.body_system == condition.body_system for symptom in case.symptoms)
    raise AssertionError("unreachable: Condition validation enforces exactly one kind")


def evaluate_rules(rules: list[RedFlagRule], case: StructuredCase) -> SafetyAssessment:
    """Evaluate every rule against the case; fired rules keep rule order."""
    fired = [
        FiredRule(rule_id=rule.id, level=rule.level, description=rule.description)
        for rule in rules
        if evaluate_condition(rule.when, case)
    ]
    highest = max(
        (fired_rule.level for fired_rule in fired),
        key=lambda level: _LEVEL_RANK[level],
        default=SafetyLevel.NONE,
    )
    return SafetyAssessment(fired_rules=fired, highest_level=highest)
