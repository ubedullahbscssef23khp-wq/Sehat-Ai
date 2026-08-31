"""Typed domain models — single source of truth (ARCHITECTURE.md §7).

Pure data definitions with validation. No framework, I/O, or LLM imports so
the safety-relevant types stay independently testable.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

__all__ = [
    "AgeGroup",
    "BodySystem",
    "Citation",
    "ClinicianSummary",
    "Condition",
    "DecisionTrace",
    "Demographics",
    "EmergencyPattern",
    "FiredRule",
    "GuidanceResponse",
    "Language",
    "LLMCallTrace",
    "LocalizedText",
    "Message",
    "MessageRole",
    "Progression",
    "RedFlagRule",
    "SafetyAssessment",
    "SafetyLevel",
    "Session",
    "SessionStatus",
    "StructuredCase",
    "SymptomReport",
    "TriageDecision",
    "TriageLevel",
]


class Language(str, Enum):
    EN = "en"
    UR = "ur"
    SD = "sd"


class AgeGroup(str, Enum):
    """Coarse buckets only — never exact ages (ARCHITECTURE.md §7)."""

    INFANT = "infant"
    CHILD = "child"
    ADOLESCENT = "adolescent"
    ADULT = "adult"
    OLDER_ADULT = "older_adult"
    UNKNOWN = "unknown"


class Progression(str, Enum):
    WORSE = "worse"
    SAME = "same"
    BETTER = "better"
    UNKNOWN = "unknown"


class BodySystem(str, Enum):
    NEUROLOGICAL = "neurological"
    CARDIOVASCULAR = "cardiovascular"
    RESPIRATORY = "respiratory"
    GASTROINTESTINAL = "gastrointestinal"
    GENITOURINARY = "genitourinary"
    MUSCULOSKELETAL = "musculoskeletal"
    SKIN = "skin"
    SYSTEMIC = "systemic"
    OTHER = "other"
    UNKNOWN = "unknown"


class SafetyLevel(str, Enum):
    NONE = "none"
    MONITOR = "monitor"
    URGENT = "urgent"
    EMERGENCY = "emergency"


class TriageLevel(str, Enum):
    EMERGENCY = "emergency"
    URGENT_SAME_DAY = "urgent_same_day"
    ROUTINE = "routine"
    SELF_CARE = "self_care"
    NEEDS_MORE_INFO = "needs_more_info"


class SessionStatus(str, Enum):
    COLLECTING = "collecting"
    ASSESSING = "assessing"
    GUIDED = "guided"
    ESCALATED = "escalated"
    CLOSED = "closed"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class LocalizedText(BaseModel):
    model_config = ConfigDict(frozen=True)

    en: str = Field(min_length=1)
    ur: str | None = None
    sd: str | None = None

    def for_language(self, language: Language) -> str:
        translated = {Language.UR: self.ur, Language.SD: self.sd}.get(language)
        return translated if translated is not None else self.en


class SymptomReport(BaseModel):
    name: str = Field(min_length=1)
    body_system: BodySystem = BodySystem.UNKNOWN
    severity: int | None = Field(default=None, ge=0, le=10)
    progression: Progression = Progression.UNKNOWN
    duration: str | None = None


class Demographics(BaseModel):
    age_group: AgeGroup | None = None
    pregnant: bool | None = None


class StructuredCase(BaseModel):
    chief_complaint: str = Field(min_length=1)
    symptoms: list[SymptomReport] = Field(default_factory=list)
    demographics: Demographics = Field(default_factory=Demographics)
    associated_factors: list[str] = Field(default_factory=list)
    red_flag_signals: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    raw_excerpt: str = ""


class Condition(BaseModel):
    """One node of a rule condition tree: exactly one kind must be set.

    Leaves evaluate against a StructuredCase; all_of/any_of combine children.
    """

    all_of: list["Condition"] | None = None
    any_of: list["Condition"] | None = None
    red_flag_signal: str | None = Field(default=None, min_length=1)
    min_severity: int | None = Field(default=None, ge=0, le=10)
    progression: Progression | None = None
    pregnant: bool | None = None
    age_group_in: list[AgeGroup] | None = Field(default=None, min_length=1)
    body_system: BodySystem | None = None

    @model_validator(mode="after")
    def _exactly_one_kind(self) -> "Condition":
        kinds = [
            name
            for name, value in (
                ("all_of", self.all_of),
                ("any_of", self.any_of),
                ("red_flag_signal", self.red_flag_signal),
                ("min_severity", self.min_severity),
                ("progression", self.progression),
                ("pregnant", self.pregnant),
                ("age_group_in", self.age_group_in),
                ("body_system", self.body_system),
            )
            if value is not None
        ]
        if len(kinds) != 1:
            raise ValueError(f"condition must set exactly one kind, got: {kinds or 'none'}")
        for combinator in ("all_of", "any_of"):
            children = getattr(self, combinator)
            if children is not None and not children:
                raise ValueError(f"{combinator} must not be empty")
        return self


class RedFlagRule(BaseModel):
    """A version-controlled safety rule; content must carry provenance."""

    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    level: SafetyLevel
    when: Condition
    source: str = Field(min_length=1)
    review_date: date

    @model_validator(mode="after")
    def _level_above_none(self) -> "RedFlagRule":
        if self.level == SafetyLevel.NONE:
            raise ValueError("a red-flag rule must carry a level above NONE")
        return self


class FiredRule(BaseModel):
    rule_id: str
    level: SafetyLevel
    description: str


class EmergencyPattern(BaseModel):
    """A curated emergency pre-screen pattern (ARCHITECTURE.md §6 step 2, §8).

    Matching is deterministic (case-insensitive substring). Content must come
    from authoritative curation with provenance — never invented.
    """

    id: str = Field(min_length=1)
    pattern: str = Field(min_length=1)
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)
    review_date: date


class SafetyAssessment(BaseModel):
    fired_rules: list[FiredRule] = Field(default_factory=list)
    highest_level: SafetyLevel = SafetyLevel.NONE


class TriageDecision(BaseModel):
    level: TriageLevel
    fired_rule_ids: list[str] = Field(default_factory=list)
    next_actions: list[LocalizedText] = Field(min_length=1)
    self_care_limits: list[LocalizedText] = Field(default_factory=list)
    recheck_advice: LocalizedText | None = None
    limited_confidence: bool = False


class Citation(BaseModel):
    source: str = Field(min_length=1)
    date_reviewed: date
    snippet: str = ""


class Session(BaseModel):
    id: str = Field(min_length=1)
    created_at: datetime
    preferred_language: Language = Language.EN
    status: SessionStatus = SessionStatus.COLLECTING


class Message(BaseModel):
    id: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    role: MessageRole
    text: str = Field(min_length=1)
    lang: Language = Language.EN
    created_at: datetime


class LLMCallTrace(BaseModel):
    model: str
    template_id: str
    latency_ms: int = Field(ge=0)
    valid: bool


class DecisionTrace(BaseModel):
    step: str = Field(min_length=1)
    timestamp: datetime
    input_hash: str | None = None
    rule_ids: list[str] = Field(default_factory=list)
    llm_calls: list[LLMCallTrace] = Field(default_factory=list)
    outputs: dict[str, Any] = Field(default_factory=dict)


class ClinicianSummary(BaseModel):
    structured_case: StructuredCase
    fired_rules: list[FiredRule] = Field(default_factory=list)
    triage_decision: TriageDecision
    timeline: list[str] = Field(default_factory=list)
    generated_at: datetime
    model_attribution: str | None = None


class GuidanceResponse(BaseModel):
    session_id: str
    user_message: LocalizedText
    triage: TriageDecision
    follow_up_questions: list[LocalizedText] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)
    disclaimers: list[LocalizedText] = Field(min_length=1)
    clinician_summary: ClinicianSummary | None = None
