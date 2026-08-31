"""Version-controlled knowledge content directory (ARCHITECTURE.md §9)."""

from __future__ import annotations

from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = KNOWLEDGE_DIR / "content"
