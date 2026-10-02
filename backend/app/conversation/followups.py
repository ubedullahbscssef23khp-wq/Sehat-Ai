"""Follow-up question phrasing (ARCHITECTURE.md §6 step 5, §8).

Field selection is deterministic (see completeness.py); the LLM only phrases
the questions. Any unusable model output falls back to deterministic
templated questions, so follow-ups never depend on LLM availability.
"""

from __future__ import annotations

import time
from collections.abc import Sequence

from app.conversation.output_policy import find_violations
from app.llm.jsonutils import parse_json_value
from app.llm.provider import LLMProvider, LLMUnavailableError
from app.llm.templates import FOLLOWUP_TEMPLATE_ID, TemplateRegistry, default_registry
from app.llm.trace import TraceCollector
from app.llm.types import LLMRequest
from app.models import Language, LocalizedText

_FALLBACK_QUESTIONS: dict[str, LocalizedText] = {
    "symptoms": LocalizedText(
        en="Please describe the main symptoms: what do you feel, where, how severe (0-10), and for how long?",
        ur="براہ کرم اہم علامات بیان کریں: آپ کیا محسوس کرتے ہیں، کہاں، شدت (0-10)، اور کتنے عرصے سے؟",
        sd="مهرباني ڪري مکيه علامتون بيان ڪريو: توهان ڇا ٿا محسوس ڪريو، ڪٿي، شدت (0-10)، ۽ ڪيتري وقت کان؟"
    ),
    "demographics.age_group": LocalizedText(
        en="What is the person's age group: infant, child, adolescent, adult, or older adult?",
        ur="مریض کی عمر کا گروپ کیا ہے: نوزائیدہ، بچہ، نوعمر، بالغ، یا عمر رسیدہ؟",
        sd="مريض جي عمر جو گروپ ڇا آهي: نئون ڄاول، ٻار، نوجوان، بالغ، يا وڏي عمر جو؟"
    ),
    "demographics.pregnant": LocalizedText(
        en="Is there any possibility the person is pregnant?",
        ur="کیا اس بات کا کوئی امکان ہے کہ مریضہ حاملہ ہیں؟",
        sd="ڇا ان ڳالهه جو ڪو امڪان آهي ته مريضه حامله آهي؟"
    )
}

def _fallback_questions(fields: Sequence[str]) -> list[LocalizedText]:
    out = []
    for field in fields:
        if field in _FALLBACK_QUESTIONS:
            out.append(_FALLBACK_QUESTIONS[field])
        else:
            out.append(LocalizedText(
                en=f"Can you tell me more about: {field}?",
                ur=f"براہ کرم اس کے بارے میں مزید بتائیں: {field}",
                sd=f"مهرباني ڪري هن جي باري ۾ وڌيڪ ٻڌايو: {field}"
            ))
    return out


def _parse_questions(raw: str, expected: int) -> list[str] | None:
    try:
        payload = parse_json_value(raw)
    except ValueError:
        return None
    if not isinstance(payload, list) or len(payload) != expected:
        return None
    questions: list[str] = []
    for item in payload:
        if not isinstance(item, str) or not item.strip():
            return None
        questions.append(item.strip())
    return questions


class FollowUpPhraser:
    def __init__(self, provider: LLMProvider, templates: TemplateRegistry | None = None) -> None:
        self._provider = provider
        self._templates = templates if templates is not None else default_registry()
        self._template = self._templates.get(FOLLOWUP_TEMPLATE_ID)

    async def phrase(
        self,
        fields: Sequence[str],
        language: Language,
        collector: TraceCollector,
    ) -> tuple[list[LocalizedText], bool]:
        """Return (questions, used_fallback); every attempt is traced."""
        if not fields:
            return [], False
        topics = "\n".join(f"- {field}" for field in fields)
        messages = self._template.render(topics=topics, language=language.value)
        request = LLMRequest(
            model=self._provider.model_name, messages=messages, temperature=0.3
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
            return _fallback_questions(fields), True
        latency_ms = int((time.perf_counter() - started) * 1000)
        questions = _parse_questions(response.text, expected=len(fields))
        if questions is None:
            collector.record(
                model=response.model,
                template_id=self._template.template_id,
                latency_ms=latency_ms,
                valid=False,
            )
            return _fallback_questions(fields), True
        violations = [
            violation for question in questions for violation in find_violations(question)
        ]
        if violations:
            collector.record(
                model=response.model,
                template_id=self._template.template_id,
                latency_ms=latency_ms,
                valid=False,
            )
            return _fallback_questions(fields), True
        collector.record(
            model=response.model,
            template_id=self._template.template_id,
            latency_ms=latency_ms,
            valid=True,
        )
        out = []
        for i, q in enumerate(questions):
            field = fields[i] if i < len(fields) else ""
            fallback_en = _FALLBACK_QUESTIONS[field].en if field in _FALLBACK_QUESTIONS else f"Can you tell me more about: {field}?"
            if language == Language.UR:
                out.append(LocalizedText(en=fallback_en, ur=q))
            elif language == Language.SD:
                out.append(LocalizedText(en=fallback_en, sd=q))
            else:
                out.append(LocalizedText(en=q))
        return out, False
