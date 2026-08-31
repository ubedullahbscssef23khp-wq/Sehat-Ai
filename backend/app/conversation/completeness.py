"""Deterministic completeness check (ARCHITECTURE.md §6 step 5).

The fields to ask about are computed from the structured data — the LLM may
phrase the questions but can neither skip nor add required fields. These are
schema-completeness requirements, not clinical claims.
"""

from __future__ import annotations

from app.models import StructuredCase


def missing_required_fields(case: StructuredCase) -> list[str]:
    missing: list[str] = []
    if not case.symptoms:
        missing.append("symptoms")
    if case.demographics.age_group is None:
        missing.append("demographics.age_group")
    if case.demographics.pregnant is None:
        missing.append("demographics.pregnant")
    return missing
