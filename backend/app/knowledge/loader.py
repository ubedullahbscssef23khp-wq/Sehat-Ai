"""Load curated knowledge entries with provenance enforcement (ARCHITECTURE.md §9).

Each entry is one Markdown file with a YAML frontmatter block:

    ---
    id: dehydration-general
    title: Dehydration — general information
    terms: [dehydration, thirst, dry mouth]
    source: <authoritative public health source>
    date_reviewed: 2026-01-15
    ---
    Curated body text shown to users as a cited snippet.

Provenance is mandatory: an entry missing `source` or `date_reviewed` (or with
any structural problem) rejects the whole file, so un-cited content can never
partially enter the corpus. Content is curated from authoritative public
sources — never invented, never model-generated.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from app.models import KnowledgeEntry

__all__ = [
    "KnowledgeLoadError",
    "parse_entry",
    "load_entry_file",
    "load_entries_dir",
]

_FRONTMATTER_DELIMITER = "---"


class KnowledgeLoadError(Exception):
    """A knowledge file is structurally invalid and must not be partially loaded."""


def _split_frontmatter(text: str, origin: str) -> tuple[str, str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != _FRONTMATTER_DELIMITER:
        raise KnowledgeLoadError(f"{origin}: file must start with a '---' frontmatter block")
    for index in range(1, len(lines)):
        if lines[index].strip() == _FRONTMATTER_DELIMITER:
            frontmatter = "\n".join(lines[1:index])
            body = "\n".join(lines[index + 1 :])
            return frontmatter, body
    raise KnowledgeLoadError(f"{origin}: frontmatter block is not closed with '---'")


def parse_entry(frontmatter: str, body: str, origin: str) -> KnowledgeEntry:
    try:
        meta: Any = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        raise KnowledgeLoadError(f"{origin}: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(meta, dict):
        raise KnowledgeLoadError(f"{origin}: frontmatter must be a YAML mapping")
    if not body.strip():
        raise KnowledgeLoadError(f"{origin}: entry body must not be empty")
    meta = dict(meta)
    meta["content"] = body.strip()
    try:
        return KnowledgeEntry.model_validate(meta)
    except ValidationError as exc:
        raise KnowledgeLoadError(f"{origin}: entry is invalid:\n{exc}") from exc


def load_entry_file(path: Path) -> KnowledgeEntry:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise KnowledgeLoadError(f"{path.name}: unreadable file: {exc}") from exc
    frontmatter, body = _split_frontmatter(text, path.name)
    return parse_entry(frontmatter, body, path.name)


def load_entries_dir(directory: Path) -> list[KnowledgeEntry]:
    entries: list[KnowledgeEntry] = []
    seen: set[str] = set()
    for path in sorted(directory.glob("*.md")):
        if path.stem.casefold() == "readme":
            continue
        entry = load_entry_file(path)
        if entry.id in seen:
            raise KnowledgeLoadError(f"{path.name}: duplicate entry id {entry.id!r}")
        seen.add(entry.id)
        entries.append(entry)
    return entries
