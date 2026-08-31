"""Decision-trace collection for LLM-mediated steps (ARCHITECTURE.md §4, §7).

Every LLM call is recorded with model, template ID, latency, and validity so
each AI-mediated decision is reconstructable afterwards.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from app.models import DecisionTrace, LLMCallTrace

__all__ = ["TraceCollector"]


class TraceCollector:
    def __init__(self, step: str, input_hash: str | None = None) -> None:
        self._step = step
        self._input_hash = input_hash
        self._calls: list[LLMCallTrace] = []

    @property
    def calls(self) -> list[LLMCallTrace]:
        return list(self._calls)

    def record(self, *, model: str, template_id: str, latency_ms: int, valid: bool) -> None:
        self._calls.append(
            LLMCallTrace(model=model, template_id=template_id, latency_ms=latency_ms, valid=valid)
        )

    def finalize(self, outputs: dict[str, Any]) -> DecisionTrace:
        return DecisionTrace(
            step=self._step,
            timestamp=datetime.now(timezone.utc),
            input_hash=self._input_hash,
            llm_calls=self.calls,
            outputs=outputs,
        )
