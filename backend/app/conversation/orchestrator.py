"""Conversation orchestration: the session state machine over the safety core.

Flow per ARCHITECTURE.md §6: emergency pre-screen -> structured extraction ->
deterministic safety assessment -> deterministic completeness -> deterministic
triage -> response. The LLM participates only in extraction and question
phrasing; it never decides triage, and safety flags always outrank
completeness (an emergency is never delayed by follow-up questions).
"""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

from app.conversation.completeness import missing_required_fields
from app.conversation.composition import ResponseComposer
from app.conversation.errors import SessionClosedError, SessionNotFoundError
from app.conversation.followups import FollowUpPhraser
from app.conversation.responses import NO_EVIDENCE_NOTE, build_guidance, build_rephrase_guidance
from app.conversation.summary import build_clinician_summary
from app.extraction.service import ExtractionService
from app.knowledge.retrieval import LexicalKnowledgeRetriever
from app.llm.provider import LLMProvider, LLMUnavailableError
from app.llm.templates import TemplateRegistry
from app.llm.trace import TraceCollector
from app.models import (
    DecisionTrace,
    EmergencyPattern,
    FiredRule,
    GuidanceResponse,
    KnowledgeEntry,
    Language,
    LocalizedText,
    Message,
    MessageRole,
    RedFlagRule,
    SafetyAssessment,
    SafetyLevel,
    Session,
    SessionStatus,
    StructuredCase,
    TriageLevel,
)
from app.persistence.repositories import (
    CaseRepository,
    MessageRepository,
    SessionRepository,
    TraceRepository,
)
from app.safety.engine import evaluate_rules
from app.safety.prescreen import evaluate_prescreen
from app.triage.engine import decide

__all__ = ["ConversationOrchestrator"]

_ESCALATED_LEVELS = (TriageLevel.EMERGENCY, TriageLevel.URGENT_SAME_DAY)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex


class ConversationOrchestrator:
    def __init__(
        self,
        *,
        provider: LLMProvider,
        session_factory: sessionmaker[SASession],
        rules: list[RedFlagRule],
        prescreen_patterns: list[EmergencyPattern],
        max_followup_rounds: int,
        knowledge: Sequence[KnowledgeEntry] = (),
        templates: TemplateRegistry | None = None,
    ) -> None:
        self._sessions = SessionRepository(session_factory)
        self._messages = MessageRepository(session_factory)
        self._cases = CaseRepository(session_factory)
        self._traces = TraceRepository(session_factory)
        self._extraction = ExtractionService(provider, templates)
        self._phraser = FollowUpPhraser(provider, templates)
        self._composer = ResponseComposer(provider, templates)
        self._retriever = LexicalKnowledgeRetriever(knowledge)
        self._rules = rules
        self._patterns = prescreen_patterns
        self._max_followup_rounds = max_followup_rounds

    def create_session(self, preferred_language: Language = Language.EN) -> Session:
        session = Session(
            id=_new_id(), created_at=_now(), preferred_language=preferred_language
        )
        self._sessions.create(session)
        return session

    def get_session(self, session_id: str) -> Session | None:
        return self._sessions.get(session_id)

    async def handle_message(self, session_id: str, text: str) -> GuidanceResponse:
        session = self._sessions.get(session_id)
        if session is None:
            raise SessionNotFoundError(session_id)
        if session.status is SessionStatus.CLOSED:
            raise SessionClosedError(session_id)

        user_message = Message(
            id=_new_id(),
            session_id=session_id,
            role=MessageRole.USER,
            text=text,
            lang=session.preferred_language,
            created_at=_now(),
        )
        self._messages.append(user_message)
        input_hash = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()

        # Step 2: deterministic emergency pre-screen — before any LLM work.
        matched = evaluate_prescreen(self._patterns, text)
        if matched:
            self._traces.append(
                session_id,
                DecisionTrace(
                    step="prescreen",
                    timestamp=_now(),
                    input_hash=input_hash,
                    rule_ids=[pattern.id for pattern in matched],
                ),
            )
            assessment = SafetyAssessment(
                fired_rules=[
                    FiredRule(
                        rule_id=pattern.id,
                        level=SafetyLevel.EMERGENCY,
                        description=pattern.description,
                    )
                    for pattern in matched
                ],
                highest_level=SafetyLevel.EMERGENCY,
            )
            decision = decide(StructuredCase(chief_complaint=text.strip()), assessment)
            self._sessions.set_status(session_id, SessionStatus.ESCALATED)
            return build_guidance(session_id, decision)

        # Step 3: structured extraction (LLM; language understanding only).
        history = tuple(
            message
            for message in self._messages.list_for_session(session_id)
            if message.id != user_message.id
        )
        self._sessions.set_status(session_id, SessionStatus.ASSESSING)
        try:
            outcome = await self._extraction.extract(text, history=history)
        except LLMUnavailableError:
            self._sessions.set_status(session_id, session.status)
            raise
        self._traces.append(session_id, outcome.trace)

        if outcome.case is None:
            self._sessions.set_status(session_id, SessionStatus.COLLECTING)
            return build_rephrase_guidance(session_id)
        case = outcome.case

        # Step 5 (field selection): completeness is computed deterministically;
        # the model's own gap report is never trusted.
        fields = missing_required_fields(case)
        case = case.model_copy(update={"missing_fields": fields})
        self._cases.append(session_id, case)

        # Step 4: deterministic safety assessment (pure rules, no LLM).
        assessment = evaluate_rules(self._rules, case)
        self._traces.append(
            session_id,
            DecisionTrace(
                step="safety",
                timestamp=_now(),
                input_hash=input_hash,
                rule_ids=[fired.rule_id for fired in assessment.fired_rules],
                outputs={"highest_level": assessment.highest_level.value},
            ),
        )

        # Step 6: deterministic triage.
        decision = decide(case, assessment)
        follow_ups: tuple[LocalizedText, ...] = ()
        if decision.level is TriageLevel.NEEDS_MORE_INFO:
            if self._sessions.followup_rounds(session_id) < self._max_followup_rounds:
                collector = TraceCollector(step="followup_phrasing", input_hash=input_hash)
                questions, used_fallback = await self._phraser.phrase(
                    fields, session.preferred_language, collector
                )
                self._traces.append(
                    session_id,
                    collector.finalize({"fields": fields, "fallback_used": used_fallback}),
                )
                follow_ups = tuple(questions)
                self._sessions.increment_followup_rounds(session_id)
                self._sessions.set_status(session_id, SessionStatus.COLLECTING)
            else:
                decision = decide(case, assessment, best_effort=True)

        self._traces.append(
            session_id,
            DecisionTrace(
                step="triage",
                timestamp=_now(),
                input_hash=input_hash,
                rule_ids=decision.fired_rule_ids,
                outputs={
                    "level": decision.level.value,
                    "limited_confidence": decision.limited_confidence,
                },
            ),
        )

        if follow_ups:
            return build_guidance(session_id, decision, follow_ups)

        final_status = (
            SessionStatus.ESCALATED
            if decision.level in _ESCALATED_LEVELS
            else SessionStatus.GUIDED
        )
        self._sessions.set_status(session_id, final_status)

        # Step 7: knowledge retrieval — deterministic over curated content;
        # an empty result is reported honestly, never filled with model memory.
        retrieved = self._retriever.retrieve(case)
        evidence = [entry.citation() for entry in retrieved]
        evidence_note = None if evidence else NO_EVIDENCE_NOTE
        self._traces.append(
            session_id,
            DecisionTrace(
                step="knowledge_retrieval",
                timestamp=_now(),
                input_hash=input_hash,
                outputs={"entry_ids": [entry.id for entry in retrieved]},
            ),
        )

        # Step 8: response composition — LLM phrasing only, constrained to the
        # triage output and evidence, behind the output-policy filter with a
        # deterministic templated fallback.
        collector = TraceCollector(step="response_composition", input_hash=input_hash)
        composed_text, used_fallback, violations = await self._composer.compose(
            decision=decision,
            evidence=evidence,
            language=session.preferred_language,
            collector=collector,
        )
        self._traces.append(
            session_id,
            collector.finalize({"fallback_used": used_fallback, "violations": violations}),
        )

        # Phase 9: Build clinician-ready summary from validated state.
        all_messages = self._messages.list_for_session(session_id)
        clinician_summary = build_clinician_summary(
            case=case,
            fired_rules=assessment.fired_rules,
            triage_decision=decision,
            messages=all_messages,
            model_attribution=None,  # Model attribution will be added if provider info becomes available.
        )

        return build_guidance(
            session_id,
            decision,
            user_message=None if used_fallback else LocalizedText(en=composed_text),
            evidence=evidence,
            evidence_note=evidence_note,
            clinician_summary=clinician_summary,
        )
