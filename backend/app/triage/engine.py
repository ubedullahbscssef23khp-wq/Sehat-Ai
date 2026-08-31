"""Deterministic triage-level computation (ARCHITECTURE.md §6 step 6, §8).

Pure function of the structured case plus the safety assessment. Safety flags
always take precedence over information completeness: an emergency or urgent
flag must never be delayed by follow-up questions.
"""

from __future__ import annotations

from app.models import (
    LocalizedText,
    SafetyAssessment,
    SafetyLevel,
    StructuredCase,
    TriageDecision,
    TriageLevel,
)

# Generic care-seeking copy per level. These are product safety statements,
# not clinical claims; localized variants are added in Phase 6.
_ACTIONS: dict[TriageLevel, list[LocalizedText]] = {
    TriageLevel.EMERGENCY: [
        LocalizedText(en="Call emergency services or go to the nearest emergency department now."),
        LocalizedText(en="Do not wait to see if the symptoms settle on their own."),
    ],
    TriageLevel.URGENT_SAME_DAY: [
        LocalizedText(en="Arrange an in-person assessment with a healthcare professional today."),
    ],
    TriageLevel.ROUTINE: [
        LocalizedText(en="Arrange a non-urgent appointment with a healthcare professional to review these symptoms."),
    ],
    TriageLevel.SELF_CARE: [
        LocalizedText(en="Self-care at home is reasonable based on the information provided."),
    ],
    TriageLevel.NEEDS_MORE_INFO: [
        LocalizedText(en="Answer the follow-up questions so the guidance can be completed."),
    ],
}

_SELF_CARE_LIMITS: list[LocalizedText] = [
    LocalizedText(en="Seek medical care if symptoms worsen, new symptoms appear, or you are concerned."),
]

_RECHECK_ADVICE = LocalizedText(
    en="If symptoms worsen, persist, or you become concerned, seek medical care promptly."
)


def decide(case: StructuredCase, assessment: SafetyAssessment) -> TriageDecision:
    levels = {fired.level for fired in assessment.fired_rules}

    if SafetyLevel.EMERGENCY in levels:
        level = TriageLevel.EMERGENCY
    elif SafetyLevel.URGENT in levels:
        level = TriageLevel.URGENT_SAME_DAY
    elif case.missing_fields:
        level = TriageLevel.NEEDS_MORE_INFO
    elif SafetyLevel.MONITOR in levels:
        level = TriageLevel.ROUTINE
    else:
        level = TriageLevel.SELF_CARE

    return TriageDecision(
        level=level,
        fired_rule_ids=[fired.rule_id for fired in assessment.fired_rules],
        next_actions=_ACTIONS[level],
        self_care_limits=list(_SELF_CARE_LIMITS) if level == TriageLevel.SELF_CARE else [],
        recheck_advice=_RECHECK_ADVICE
        if level in (TriageLevel.SELF_CARE, TriageLevel.ROUTINE)
        else None,
    )
