"""Shared helpers for Phase 1 tests.

Fixtures are synthetic and structural (stable T-* IDs, numeric conditions):
they exercise engine mechanics only and are NOT medical content.
"""

from __future__ import annotations

from datetime import date

from app.models import Condition, RedFlagRule, SafetyLevel, StructuredCase

SYNTHETIC_SOURCE = "synthetic test fixture (not medical content)"


def make_case(**overrides) -> StructuredCase:
    base: dict = {"chief_complaint": "synthetic test complaint"}
    base.update(overrides)
    return StructuredCase(**base)


def make_rule(rule_id: str, level: SafetyLevel, condition: Condition, **overrides) -> RedFlagRule:
    base: dict = {
        "id": rule_id,
        "description": f"synthetic rule {rule_id}",
        "level": level,
        "when": condition,
        "source": SYNTHETIC_SOURCE,
        "review_date": date(2026, 1, 1),
    }
    base.update(overrides)
    return RedFlagRule(**base)
