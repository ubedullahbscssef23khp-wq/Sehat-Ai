"""Version-controlled safety content directories (ARCHITECTURE.md §8)."""

from __future__ import annotations

from pathlib import Path

SAFETY_DIR = Path(__file__).resolve().parent
RULES_DIR = SAFETY_DIR / "rules"
PRESCREEN_DIR = SAFETY_DIR / "prescreen_patterns"
