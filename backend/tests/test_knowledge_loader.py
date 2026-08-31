"""Knowledge loader tests (Phase 4 acceptance: provenance enforcement).

Entries here are synthetic fixtures, not medical content.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from app.knowledge.loader import (
    KnowledgeLoadError,
    load_entries_dir,
    load_entry_file,
    parse_entry,
)
from app.knowledge.paths import CONTENT_DIR

VALID_FRONTMATTER = """\
---
id: t-kb-1
title: Synthetic topic
terms: [synthetic-symptom, synthetic topic]
source: synthetic authoritative source
date_reviewed: 2026-01-15
---
Synthetic curated body content.
"""


def write_entry(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def test_valid_entry_round_trip(tmp_path: Path) -> None:
    entry = load_entry_file(write_entry(tmp_path, "t-kb-1.md", VALID_FRONTMATTER))
    assert entry.id == "t-kb-1"
    assert entry.title == "Synthetic topic"
    assert entry.terms == ["synthetic-symptom", "synthetic topic"]
    assert entry.content == "Synthetic curated body content."
    assert entry.source == "synthetic authoritative source"
    assert entry.date_reviewed == date(2026, 1, 15)


def test_entry_without_source_fails_to_load(tmp_path: Path) -> None:
    text = VALID_FRONTMATTER.replace("source: synthetic authoritative source\n", "")
    with pytest.raises(KnowledgeLoadError):
        load_entry_file(write_entry(tmp_path, "no-source.md", text))


def test_entry_without_date_reviewed_fails_to_load(tmp_path: Path) -> None:
    text = VALID_FRONTMATTER.replace("date_reviewed: 2026-01-15\n", "")
    with pytest.raises(KnowledgeLoadError):
        load_entry_file(write_entry(tmp_path, "no-date.md", text))


def test_entry_with_blank_source_fails_to_load(tmp_path: Path) -> None:
    text = VALID_FRONTMATTER.replace("source: synthetic authoritative source", "source: ''")
    with pytest.raises(KnowledgeLoadError):
        load_entry_file(write_entry(tmp_path, "blank-source.md", text))


def test_missing_frontmatter_rejected(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeLoadError, match="frontmatter"):
        load_entry_file(write_entry(tmp_path, "plain.md", "just body text"))


def test_unclosed_frontmatter_rejected(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeLoadError, match="not closed"):
        load_entry_file(write_entry(tmp_path, "unclosed.md", "---\nid: x\nbody with no close"))


def test_frontmatter_must_be_mapping(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeLoadError, match="mapping"):
        load_entry_file(write_entry(tmp_path, "list.md", "---\n- a\n- b\n---\nbody"))


def test_invalid_yaml_frontmatter_rejected(tmp_path: Path) -> None:
    with pytest.raises(KnowledgeLoadError, match="YAML"):
        load_entry_file(write_entry(tmp_path, "bad.md", "---\nid: [unclosed\n---\nbody"))


def test_empty_body_rejected(tmp_path: Path) -> None:
    text = VALID_FRONTMATTER.replace("Synthetic curated body content.\n", "\n")
    with pytest.raises(KnowledgeLoadError, match="body"):
        load_entry_file(write_entry(tmp_path, "empty-body.md", text))


def test_parse_entry_rejects_missing_fields() -> None:
    with pytest.raises(KnowledgeLoadError):
        parse_entry("id: x\ntitle: t", "body", "inline")


def test_load_dir_rejects_duplicate_ids(tmp_path: Path) -> None:
    write_entry(tmp_path, "a.md", VALID_FRONTMATTER)
    write_entry(tmp_path, "b.md", VALID_FRONTMATTER)
    with pytest.raises(KnowledgeLoadError, match="duplicate"):
        load_entries_dir(tmp_path)


def test_load_dir_keeps_sorted_order(tmp_path: Path) -> None:
    write_entry(tmp_path, "b.md", VALID_FRONTMATTER.replace("t-kb-1", "t-kb-2"))
    write_entry(tmp_path, "a.md", VALID_FRONTMATTER)
    entries = load_entries_dir(tmp_path)
    assert [entry.id for entry in entries] == ["t-kb-1", "t-kb-2"]


def test_load_empty_dir_returns_empty_list(tmp_path: Path) -> None:
    assert load_entries_dir(tmp_path) == []


def test_shipped_corpus_is_empty_of_entries() -> None:
    """The repo must not ship invented knowledge content: only the curation
    README is present until authoritative content is curated."""
    assert load_entries_dir(CONTENT_DIR) == []
    assert (CONTENT_DIR / "README.md").exists()
