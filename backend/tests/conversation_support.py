"""Shared builders for Phase 3 tests.

All fixtures are synthetic and structural (stable T-* style IDs, numeric
placeholders): they exercise orchestration mechanics only and are NOT medical
content.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session as SASession
from sqlalchemy.orm import sessionmaker

from app.conversation.orchestrator import ConversationOrchestrator
from app.llm.mock import MockProvider
from app.llm.provider import LLMProvider
from app.models import Condition, EmergencyPattern, KnowledgeEntry, RedFlagRule, SafetyLevel
from app.persistence.database import build_engine, init_db

SYNTHETIC_SOURCE = "synthetic test fixture (not medical content)"


def complete_case_payload() -> dict:
    """A StructuredCase payload that is complete for the deterministic
    completeness check (symptoms present, age_group and pregnant known)."""
    return {
        "chief_complaint": "synthetic test complaint",
        "symptoms": [
            {
                "name": "synthetic-symptom",
                "body_system": "systemic",
                "severity": 3,
                "progression": "same",
                "duration": "2 days",
            }
        ],
        "demographics": {"age_group": "adult", "pregnant": False},
        "associated_factors": [],
        "red_flag_signals": [],
        "missing_fields": [],
        "confidence": 0.9,
        "raw_excerpt": "synthetic test complaint",
    }


def incomplete_case_payload(missing_age: bool = True) -> dict:
    """Symptoms present but demographics incomplete, so the deterministic
    completeness check asks follow-ups."""
    payload = complete_case_payload()
    if missing_age:
        payload["demographics"] = {"age_group": None, "pregnant": False}
    return payload


def case_json(**overrides) -> str:
    payload = complete_case_payload()
    payload.update(overrides)
    return json.dumps(payload)


def incomplete_case_json(**demographics: object) -> str:
    payload = complete_case_payload()
    payload["demographics"] = {"age_group": None, "pregnant": False}
    payload["demographics"].update(demographics)
    return json.dumps(payload)


def questions_json(count: int) -> str:
    return json.dumps([f"synthetic question {i + 1}?" for i in range(count)])


def make_pattern(pattern_id: str = "T-PRESCREEN-1", text: str = "synthetic-chest-pain") -> EmergencyPattern:
    return EmergencyPattern(
        id=pattern_id,
        pattern=text,
        description=f"synthetic prescreen pattern {pattern_id}",
        source=SYNTHETIC_SOURCE,
        review_date=date(2026, 1, 1),
    )


def make_signal_rule(rule_id: str, signal: str, level: SafetyLevel) -> RedFlagRule:
    return RedFlagRule(
        id=rule_id,
        description=f"synthetic rule {rule_id}",
        level=level,
        when=Condition(red_flag_signal=signal),
        source=SYNTHETIC_SOURCE,
        review_date=date(2026, 1, 1),
    )


def make_knowledge_entry(
    entry_id: str = "T-KB-1",
    terms: tuple[str, ...] = ("synthetic-symptom",),
) -> KnowledgeEntry:
    return KnowledgeEntry(
        id=entry_id,
        title=f"Synthetic topic {entry_id}",
        terms=list(terms),
        content=f"Synthetic curated content for {entry_id}.",
        source=SYNTHETIC_SOURCE,
        date_reviewed=date(2026, 1, 1),
    )


class OrchestratorHarness:
    """Orchestrator over a file-backed SQLite DB plus repository access."""

    def __init__(
        self,
        tmp_path: Path,
        scripts: tuple[str, ...] = (),
        provider: LLMProvider | None = None,
        rules: list[RedFlagRule] | None = None,
        patterns: list[EmergencyPattern] | None = None,
        knowledge: list[KnowledgeEntry] | None = None,
        max_followup_rounds: int = 2,
    ) -> None:
        self.provider: LLMProvider
        if provider is not None:
            self.provider = provider
        else:
            self.provider = MockProvider(scripts)
        engine = build_engine(tmp_path / "test.sqlite")
        init_db(engine)
        self.session_factory: sessionmaker[SASession] = sessionmaker(
            bind=engine, expire_on_commit=False, future=True
        )
        self.orchestrator = ConversationOrchestrator(
            provider=self.provider,
            session_factory=self.session_factory,
            rules=rules or [],
            prescreen_patterns=patterns or [],
            max_followup_rounds=max_followup_rounds,
            knowledge=knowledge or [],
        )
        self.db_path = tmp_path / "test.sqlite"
