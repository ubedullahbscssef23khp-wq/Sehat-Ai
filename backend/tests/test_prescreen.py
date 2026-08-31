"""Emergency pre-screen engine + pattern loader tests (Phase 3).

Patterns here are synthetic fixtures, not medical content. The production
pattern directory ships empty on purpose: content must be curated from
authoritative sources, never invented.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from app.models import EmergencyPattern
from app.safety.loader import RuleLoadError, parse_patterns
from app.safety.paths import PRESCREEN_DIR
from app.safety.prescreen import evaluate_prescreen


def make_pattern(pattern_id: str, text: str) -> EmergencyPattern:
    return EmergencyPattern(
        id=pattern_id,
        pattern=text,
        description=f"synthetic pattern {pattern_id}",
        source="synthetic test fixture (not medical content)",
        review_date=date(2026, 1, 1),
    )


def test_prescreen_is_case_insensitive_substring_match() -> None:
    patterns = [make_pattern("p1", "chest pain")]
    matched = evaluate_prescreen(patterns, "I have severe CHEST PAIN since morning")
    assert [pattern.id for pattern in matched] == ["p1"]


def test_prescreen_no_match_returns_empty() -> None:
    patterns = [make_pattern("p1", "chest pain")]
    assert evaluate_prescreen(patterns, "I have a mild cough") == []


def test_prescreen_empty_pattern_list_never_matches() -> None:
    """Ships empty by default: with no curated patterns, nothing can trigger
    the shortcut — infrastructure without invented medical content."""
    assert evaluate_prescreen([], "any text at all") == []


def test_prescreen_keeps_pattern_order() -> None:
    patterns = [make_pattern("p1", "alpha"), make_pattern("p2", "beta")]
    matched = evaluate_prescreen(patterns, "beta and alpha")
    assert [pattern.id for pattern in matched] == ["p1", "p2"]


def test_parse_patterns_requires_patterns_list() -> None:
    with pytest.raises(RuleLoadError):
        parse_patterns({"rules": []}, "test.yaml")


def test_parse_patterns_rejects_invalid_entry() -> None:
    with pytest.raises(RuleLoadError):
        parse_patterns({"patterns": [{"id": "p1"}]}, "test.yaml")


def test_parse_patterns_rejects_duplicate_ids() -> None:
    data = {
        "patterns": [
            {
                "id": "p1",
                "pattern": "a",
                "description": "d",
                "source": "s",
                "review_date": "2026-01-01",
            },
            {
                "id": "p1",
                "pattern": "b",
                "description": "d",
                "source": "s",
                "review_date": "2026-01-01",
            },
        ]
    }
    with pytest.raises(RuleLoadError, match="duplicate"):
        parse_patterns(data, "test.yaml")


def test_shipped_prescreen_directory_is_empty_of_patterns() -> None:
    """The repo must not ship invented emergency keywords: only the README is
    present until authoritative curation happens."""
    yaml_files = list(PRESCREEN_DIR.glob("*.yaml")) + list(PRESCREEN_DIR.glob("*.yml"))
    assert yaml_files == []
    assert (PRESCREEN_DIR / "README.md").exists()


def test_load_patterns_dir_empty_returns_empty_list(tmp_path: Path) -> None:
    from app.safety.loader import load_patterns_dir

    assert load_patterns_dir(tmp_path) == []
