"""Load version-controlled YAML red-flag rules (ARCHITECTURE.md §8).

Rule files are data, not code: every entry is validated into a RedFlagRule,
and any structural problem (missing source/review_date, bad shape, duplicate
IDs) rejects the whole file so invalid rules can never partially apply.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.models import RedFlagRule


class RuleLoadError(Exception):
    """A rule file is structurally invalid and must not be partially applied."""


def parse_rules(data: Any, origin: str) -> list[RedFlagRule]:
    if not isinstance(data, dict) or not isinstance(data.get("rules"), list):
        raise RuleLoadError(f"{origin}: expected a top-level mapping with a 'rules' list")

    rules: list[RedFlagRule] = []
    seen: set[str] = set()
    for index, entry in enumerate(data["rules"]):
        try:
            rule = RedFlagRule.model_validate(entry)
        except ValidationError as exc:
            raise RuleLoadError(f"{origin}: rule #{index} is invalid:\n{exc}") from exc
        if rule.id in seen:
            raise RuleLoadError(f"{origin}: duplicate rule id {rule.id!r}")
        seen.add(rule.id)
        rules.append(rule)
    return rules


def load_rules_file(path: Path) -> list[RedFlagRule]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RuleLoadError(f"{path.name}: unreadable or invalid YAML: {exc}") from exc
    return parse_rules(data, path.name)


def load_rules_dir(directory: Path) -> list[RedFlagRule]:
    rules: list[RedFlagRule] = []
    seen: set[str] = set()
    paths = sorted(directory.glob("*.yaml")) + sorted(directory.glob("*.yml"))
    for path in paths:
        for rule in load_rules_file(path):
            if rule.id in seen:
                raise RuleLoadError(f"{path.name}: duplicate rule id {rule.id!r}")
            seen.add(rule.id)
            rules.append(rule)
    return rules
