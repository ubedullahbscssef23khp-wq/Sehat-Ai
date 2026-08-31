"""Structured extraction: free text -> validated StructuredCase (ARCHITECTURE.md §6 step 3).

The LLM only converts text into structure; it never decides anything. Model
output is untrusted input: it must parse as JSON and pass the StructuredCase
schema before use. On invalid output there is exactly one retry with a
correction hint; a second failure yields the graceful "please rephrase" path.
"""

from __future__ import annotations

import hashlib
import time

from pydantic import BaseModel, ValidationError

from app.llm.jsonutils import parse_json_value
from app.llm.provider import LLMProvider
from app.llm.templates import EXTRACTION_TEMPLATE_ID, TemplateRegistry, default_registry
from app.llm.trace import TraceCollector
from app.llm.types import LLMRequest
from app.models import DecisionTrace, Message, StructuredCase

__all__ = ["ExtractionOutcome", "ExtractionService"]

_STEP = "extraction"


class ExtractionOutcome(BaseModel):
    """Result of one extraction pass: a validated case, or a request to rephrase."""

    case: StructuredCase | None = None
    needs_rephrase: bool = False
    trace: DecisionTrace


def _parse_case(raw: str) -> StructuredCase:
    """Parse and validate model output; raises ValueError with a safe summary."""
    payload = parse_json_value(raw)
    if not isinstance(payload, dict):
        raise ValueError("model output must be a JSON object")
    try:
        return StructuredCase.model_validate(payload)
    except ValidationError as exc:
        fields = sorted({str(part) for error in exc.errors() for part in error["loc"][:1]})
        raise ValueError(f"model output failed schema validation for fields: {fields}") from exc


class ExtractionService:
    def __init__(self, provider: LLMProvider, templates: TemplateRegistry | None = None) -> None:
        self._provider = provider
        self._templates = templates if templates is not None else default_registry()
        self._template = self._templates.get(EXTRACTION_TEMPLATE_ID)

    async def extract(self, text: str, history: tuple[Message, ...] = ()) -> ExtractionOutcome:
        trimmed = text.strip()
        collector = TraceCollector(
            step=_STEP, input_hash=hashlib.sha256(trimmed.encode("utf-8")).hexdigest()
        )
        if not trimmed:
            return ExtractionOutcome(
                needs_rephrase=True,
                trace=collector.finalize({"status": "rephrase_needed", "reason": "empty_input"}),
            )

        rendered_history = "\n".join(
            f"{message.role.value}: {message.text}" for message in history
        ) or "(no previous conversation)"

        feedback = ""
        for _attempt in range(2):
            messages = self._template.render(
                history=rendered_history, user_text=trimmed, feedback=feedback
            )
            request = LLMRequest(
                model=self._provider.model_name, messages=messages, temperature=0.0
            )
            started = time.perf_counter()
            response = await self._provider.complete(request)
            latency_ms = int((time.perf_counter() - started) * 1000)
            try:
                case = _parse_case(response.text)
            except ValueError as exc:
                collector.record(
                    model=response.model,
                    template_id=self._template.template_id,
                    latency_ms=latency_ms,
                    valid=False,
                )
                feedback = (
                    f"Your previous reply was invalid: {exc}. "
                    "Return ONLY a valid JSON object matching the schema."
                )
                continue
            collector.record(
                model=response.model,
                template_id=self._template.template_id,
                latency_ms=latency_ms,
                valid=True,
            )
            return ExtractionOutcome(case=case, trace=collector.finalize({"status": "success"}))

        return ExtractionOutcome(
            needs_rephrase=True,
            trace=collector.finalize({"status": "rephrase_needed", "reason": "invalid_model_output"}),
        )
