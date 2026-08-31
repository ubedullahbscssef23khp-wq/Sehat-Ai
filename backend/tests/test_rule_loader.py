"""YAML rule loader tests (Phase 1 acceptance: provenance enforcement)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.models import SafetyLevel
from app.safety.loader import RuleLoadError, load_rules_dir, load_rules_file, parse_rules

VALID_RULE = """
rules:
  - id: T-001
    description: synthetic structural rule
    level: emergency
    source: synthetic test fixture
    review_date: 2026-01-01
    when:
      min_severity: 9
"""


def write(tmp_path: Path, name: str, content: str) -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def test_loads_valid_rule_file(tmp_path: Path) -> None:
    rules = load_rules_file(write(tmp_path, "rules.yaml", VALID_RULE))
    assert len(rules) == 1
    rule = rules[0]
    assert rule.id == "T-001"
    assert rule.level == SafetyLevel.EMERGENCY
    assert rule.source == "synthetic test fixture"
    assert rule.when.min_severity == 9


def test_empty_rules_list_is_valid(tmp_path: Path) -> None:
    assert load_rules_file(write(tmp_path, "empty.yaml", "rules: []")) == []


def test_missing_source_rejected(tmp_path: Path) -> None:
    content = VALID_RULE.replace("    source: synthetic test fixture\n", "")
    with pytest.raises(RuleLoadError, match="source"):
        load_rules_file(write(tmp_path, "bad.yaml", content))


def test_missing_review_date_rejected(tmp_path: Path) -> None:
    content = VALID_RULE.replace("    review_date: 2026-01-01\n", "")
    with pytest.raises(RuleLoadError, match="review_date"):
        load_rules_file(write(tmp_path, "bad.yaml", content))


def test_invalid_level_rejected(tmp_path: Path) -> None:
    content = VALID_RULE.replace("level: emergency", "level: catastrophic")
    with pytest.raises(RuleLoadError):
        load_rules_file(write(tmp_path, "bad.yaml", content))


def test_invalid_condition_rejected(tmp_path: Path) -> None:
    content = VALID_RULE.replace("      min_severity: 9", "      min_severity: 9\n      pregnant: true")
    with pytest.raises(RuleLoadError, match="exactly one kind"):
        load_rules_file(write(tmp_path, "bad.yaml", content))


def test_missing_rules_key_rejected(tmp_path: Path) -> None:
    with pytest.raises(RuleLoadError, match="rules"):
        load_rules_file(write(tmp_path, "bad.yaml", "other: []"))


def test_non_mapping_top_level_rejected(tmp_path: Path) -> None:
    with pytest.raises(RuleLoadError):
        load_rules_file(write(tmp_path, "bad.yaml", "- a\n- b"))


def test_invalid_yaml_syntax_rejected(tmp_path: Path) -> None:
    with pytest.raises(RuleLoadError, match="YAML"):
        load_rules_file(write(tmp_path, "bad.yaml", "rules: [unclosed"))


def test_duplicate_id_within_file_rejected(tmp_path: Path) -> None:
    content = """
rules:
  - id: T-001
    description: synthetic structural rule
    level: emergency
    source: synthetic test fixture
    review_date: 2026-01-01
    when:
      min_severity: 9
  - id: T-001
    description: duplicate of the first rule
    level: urgent
    source: synthetic test fixture
    review_date: 2026-01-01
    when:
      min_severity: 5
"""
    with pytest.raises(RuleLoadError, match="duplicate"):
        load_rules_file(write(tmp_path, "dup.yaml", content))


def test_load_rules_dir_sorted_and_combined(tmp_path: Path) -> None:
    write(tmp_path, "b.yaml", VALID_RULE)
    write(tmp_path, "a.yaml", VALID_RULE.replace("T-001", "T-000"))
    rules = load_rules_dir(tmp_path)
    assert [rule.id for rule in rules] == ["T-000", "T-001"]


def test_load_rules_dir_rejects_duplicate_ids_across_files(tmp_path: Path) -> None:
    write(tmp_path, "a.yaml", VALID_RULE)
    write(tmp_path, "b.yaml", VALID_RULE)
    with pytest.raises(RuleLoadError, match="duplicate"):
        load_rules_dir(tmp_path)


def test_parse_rules_accepts_mapping_directly() -> None:
    import yaml

    rules = parse_rules(yaml.safe_load(VALID_RULE), "inline")
    assert rules[0].id == "T-001"
