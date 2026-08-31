"""Deterministic output-policy filter (ARCHITECTURE.md §1, §8).

Sehat AI never diagnoses and never recommends medications. This guard is the
architectural enforcement of that boundary on final user-facing text: any
text carrying a diagnostic claim or medication advice is rejected wholesale
and replaced by safe templated copy. False positives only cost eloquence;
false negatives would cost safety, so the filter errs on the strict side.

The filter applies to LLM-produced user-facing text (composed messages,
phrased follow-ups). Curated knowledge snippets carry human provenance and
are trusted at curation time, not filtered here.
"""

from __future__ import annotations

import re

__all__ = ["find_violations", "is_compliant", "POLICY_PATTERNS"]

# (policy_id, compiled regex). IDs are stable so traces can reference them.
POLICY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    # Diagnostic claims ("you have X", suffering-from statements, diagnoses).
    ("diagnostic_you_have", re.compile(r"\byou(?:'ve|\s+have)\b", re.IGNORECASE)),
    ("diagnostic_suffering_from", re.compile(r"\bsuffer(?:s|ing)?\s+from\b", re.IGNORECASE)),
    ("diagnostic_diagnosis_word", re.compile(r"\bdiagnos(?:is|es|ed|e)\b", re.IGNORECASE)),
    ("diagnostic_condition_claim", re.compile(r"\byour\s+condition\b", re.IGNORECASE)),
    # Medication advice (directives, drug names, dosages).
    ("medication_action_take", re.compile(
        r"\b(?:take|takes|taking|use|using|start|started|stop|stopping|give|giving)\b"
        r"(?:\s+\w+){0,2}?"
        r"\s+\b(?:medicine|medication|medications|tablet|tablets|pill|pills|drug|drugs|"
        r"dose|doses|dosage|antibiotics?|inhaler|injection|syrup)\b",
        re.IGNORECASE,
    )),
    ("medication_should_take", re.compile(
        r"\b(?:should|must|can|could|need\s+to)\s+(?:take|use|try)\b", re.IGNORECASE
    )),
    ("medication_drug_names", re.compile(
        r"\b(?:paracetamol|acetaminophen|ibuprofen|aspirin|amoxicillin|azithromycin|"
        r"metformin|omeprazole|antihistamine(?:s)?)\b",
        re.IGNORECASE,
    )),
    ("medication_dosage_units", re.compile(r"\b\d+\s*(?:mg|milligrams?|ml)\b", re.IGNORECASE)),
)


def find_violations(text: str) -> list[str]:
    """Stable policy IDs violated by the text, in pattern order (no duplicates)."""
    return [policy_id for policy_id, pattern in POLICY_PATTERNS if pattern.search(text)]


def is_compliant(text: str) -> bool:
    return not find_violations(text)
