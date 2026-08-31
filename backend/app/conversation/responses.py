"""Response construction for the conversation API (ARCHITECTURE.md §7).

User-facing copy here is product safety framing, not clinical content.
Disclaimers are server-injected and mandatory: GuidanceResponse validation
rejects an empty disclaimer list, so no client can strip the boundary.
"""

from __future__ import annotations

from app.models import (
    GuidanceResponse,
    LocalizedText,
    SafetyAssessment,
    StructuredCase,
    TriageDecision,
    TriageLevel,
)
from app.triage.engine import decide

DISCLAIMER = LocalizedText(
    en=(
        "Sehat AI provides general next-step guidance only. It is not a medical "
        "diagnosis and does not replace a qualified healthcare professional."
    )
)

_USER_MESSAGES: dict[TriageLevel, LocalizedText] = {
    TriageLevel.EMERGENCY: LocalizedText(
        en="This may be an emergency. Please follow the emergency actions below now."
    ),
    TriageLevel.URGENT_SAME_DAY: LocalizedText(
        en="These symptoms should be assessed in person by a healthcare professional today."
    ),
    TriageLevel.ROUTINE: LocalizedText(
        en="These symptoms should be reviewed by a healthcare professional; this does not look urgent."
    ),
    TriageLevel.SELF_CARE: LocalizedText(
        en="Based on what you described, self-care at home is reasonable for now."
    ),
    TriageLevel.NEEDS_MORE_INFO: LocalizedText(
        en="Please answer the follow-up questions so the guidance can be completed."
    ),
}

_REPHRASE_MESSAGE = LocalizedText(
    en="I could not fully understand that message. Please describe the symptoms again in your own words."
)


def build_guidance(
    session_id: str,
    decision: TriageDecision,
    follow_up_questions: tuple[LocalizedText, ...] = (),
) -> GuidanceResponse:
    return GuidanceResponse(
        session_id=session_id,
        user_message=_USER_MESSAGES[decision.level],
        triage=decision,
        follow_up_questions=list(follow_up_questions),
        evidence=[],
        disclaimers=[DISCLAIMER],
    )


def build_rephrase_guidance(session_id: str) -> GuidanceResponse:
    """Graceful path when model output stayed unusable after one retry.

    The decision is still produced by the deterministic triage engine
    (NEEDS_MORE_INFO), never by the LLM.
    """
    placeholder = StructuredCase(chief_complaint="(awaiting rephrase)", missing_fields=["chief_complaint"])
    decision = decide(placeholder, SafetyAssessment())
    return GuidanceResponse(
        session_id=session_id,
        user_message=_REPHRASE_MESSAGE,
        triage=decision,
        follow_up_questions=[],
        evidence=[],
        disclaimers=[DISCLAIMER],
    )
