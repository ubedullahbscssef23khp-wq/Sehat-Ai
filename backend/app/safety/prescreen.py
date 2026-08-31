"""Deterministic emergency pre-screen (ARCHITECTURE.md §6 step 2, §8).

Pure function, zero LLM, zero I/O: matches curated patterns against raw user
text BEFORE any model work, so emergencies are caught even when the LLM is
down. Pattern content is curated separately with provenance; this module only
evaluates. Unknown text never matches — absence of a pattern is never a
positive signal.
"""

from __future__ import annotations

from app.models import EmergencyPattern


def evaluate_prescreen(patterns: list[EmergencyPattern], text: str) -> list[EmergencyPattern]:
    """Return the patterns whose phrase occurs in the text (case-insensitive).

    Matches keep pattern order for stable, explainable results.
    """
    folded = text.casefold()
    return [pattern for pattern in patterns if pattern.pattern.casefold() in folded]
