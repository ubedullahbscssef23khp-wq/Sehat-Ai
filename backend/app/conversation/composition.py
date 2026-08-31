"""Guided response composition (ARCHITECTURE.md §6 step 8).

The LLM only writes empathetic user-facing prose constrained to the provided
triage actions and curated evidence. Every output passes the deterministic
output-policy filter; any violation, emptiness, or provider failure falls
back to templated copy — the final text never contains diagnostic or
prescriptive claims, and a response is never left empty.
"""

from __future__ import annotations

import time
from collections.abc import Sequence

from app.conversation.output_policy import find_violations
from app.conversation.responses import fallback_user_message
from app.llm.jsonutils import strip_code_fences
from app.llm.provider import LLMProvider, LLMUnavailableError
from app.llm.templates import COMPOSITION_TEMPLATE_ID, TemplateRegistry, default_registry
from app.llm.trace import TraceCollector
from app.llm.types import LLMRequest
from app.models import Citation, Language, TriageDecision

__all__ = ["MAX_COMPOSED_CHARS", "ResponseComposer"]

MAX_COMPOSED_CHARS = 800


class ResponseComposer:
    def __init__(self, provider: LLMProvider, templates: TemplateRegistry | None = None) -> None:
        self._provider = provider
        self._templates = templates if templates is not None else default_registry()
        self._template = self._templates.get(COMPOSITION_TEMPLATE_ID)

    async def compose(
        self,
        *,
        decision: TriageDecision,
        evidence: Sequence[Citation],
        language: Language,
        collector: TraceCollector,
    ) -> tuple[str, bool, list[str]]:
        """Return (user_facing_text, used_fallback, policy_violations).

        The fallback is deterministic templated copy, so composition can
        never emit unsafe text or fail the whole turn.
        """
        fallback = fallback_user_message(decision.level).en
        actions = "\n".join(f"- {action.en}" for action in decision.next_actions)
        evidence_text = "\n\n".join(item.snippet for item in evidence) or "(none available)"
        messages = self._template.render(
            level=decision.level.value,
            actions=actions,
            evidence=evidence_text,
            language=language.value,
        )
        request = LLMRequest(
            model=self._provider.model_name, messages=messages, temperature=0.4
        )
        started = time.perf_counter()
        try:
            response = await self._provider.complete(request)
        except LLMUnavailableError:
            latency_ms = int((time.perf_counter() - started) * 1000)
            collector.record(
                model=self._provider.model_name,
                template_id=self._template.template_id,
                latency_ms=latency_ms,
                valid=False,
            )
            return fallback, True, []

        latency_ms = int((time.perf_counter() - started) * 1000)
        text = strip_code_fences(response.text).strip()
        violations = find_violations(text)
        if not text or len(text) > MAX_COMPOSED_CHARS or violations:
            collector.record(
                model=response.model,
                template_id=self._template.template_id,
                latency_ms=latency_ms,
                valid=False,
            )
            return fallback, True, violations
        collector.record(
            model=response.model,
            template_id=self._template.template_id,
            latency_ms=latency_ms,
            valid=True,
        )
        return text, False, []
