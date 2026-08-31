"""Small shared helpers for handling LLM JSON output (untrusted input)."""

from __future__ import annotations

import json
from typing import Any

__all__ = ["parse_json_value", "strip_code_fences"]


def strip_code_fences(text: str) -> str:
    """Remove a single markdown code fence wrapper if present."""
    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        stripped = "\n".join(lines).strip()
    return stripped


def parse_json_value(raw: str) -> Any:
    """Parse model output as JSON; raises ValueError with a safe summary."""
    try:
        return json.loads(strip_code_fences(raw))
    except json.JSONDecodeError as exc:
        raise ValueError(f"model output was not valid JSON ({exc.msg})") from exc
