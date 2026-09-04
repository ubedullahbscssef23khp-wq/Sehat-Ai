"""Deterministic clinician-ready summary projection (Phase 9).

Builds a ClinicianSummary from already-validated state without making
new LLM calls, performing new retrieval, recalculating triage, or adding
medical claims.

This is a REPRESENTATION LAYER ONLY: it projects existing validated
results into a clinician-ready format.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from app.models import (
    ClinicianSummary,
    FiredRule,
    Message,
    MessageRole,
    StructuredCase,
    TriageDecision,
)

__all__ = ["build_clinician_summary"]


def build_clinician_summary(
    *,
    case: StructuredCase,
    fired_rules: list[FiredRule],
    triage_decision: TriageDecision,
    messages: Sequence[Message],
    model_attribution: str | None = None,
) -> ClinicianSummary:
    """Build a deterministic clinician-ready summary from validated state.

    Arguments:
        case: The validated and already-extracted StructuredCase.
        fired_rules: The already-evaluated FiredRule results. Must not be
            recomputed here.
        triage_decision: The already-determined TriageDecision. Must not be
            recalculated here.
        messages: The persisted conversation messages for this session, in
            chronological order.
        model_attribution: Model name/version if genuinely available; else None.

    Returns:
        A ClinicianSummary that is a projection of the validated state above.

    Notes:
        - The summary never modifies any input state.
        - It does not call any LLM or retrieval functions.
        - It does not recalculate triage or rules.
        - The timeline uses only information actually present in messages,
          in their real chronological order.
        - It never infers medical information not explicitly present.
    """
    timeline = _build_timeline(messages)

    return ClinicianSummary(
        structured_case=case,
        fired_rules=list(fired_rules),
        triage_decision=triage_decision,
        timeline=timeline,
        generated_at=datetime.now(timezone.utc),
        model_attribution=model_attribution,
    )


def _build_timeline(messages: Sequence[Message]) -> list[str]:
    """Extract a chronological timeline from persisted messages.

    Uses only information actually available from persisted messages,
    in their stored order. Does not infer medical chronology, symptom onset,
    duration, or progression beyond what is explicitly present.

    Arguments:
        messages: Persisted conversation messages in chronological order.

    Returns:
        A list of string descriptions of conversation events, in order,
        or an empty list if no meaningful events are available.
    """
    if not messages:
        return []

    timeline = []
    for message in messages:
        # Record user messages only (actual symptoms/concerns), not assistant responses.
        if message.role == MessageRole.USER:
            # Create a minimal, factual entry: timestamp and first 120 chars of the message.
            timestamp_str = message.created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
            preview = message.text[:120]
            if len(message.text) > 120:
                preview = preview + "…"
            timeline.append(f"{timestamp_str}: {preview}")

    return timeline
