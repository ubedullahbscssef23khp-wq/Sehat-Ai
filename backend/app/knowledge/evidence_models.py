"""Enterprise Clinical Knowledge & Evidence Architecture Models (PHASE 30A).

ARCHITECTURE PRINCIPLE:
"AI understands. Evidence grounds. Code controls."

This module defines typed domain schemas for evidence-grounded clinical retrieval
and synthesis. These models specify metadata, provenance, integrity, freshness,
and abstention boundaries.

NO CLINICAL CONTENT IS CREATED OR ACTIVATED BY THIS MODULE.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from enum import Enum
import hashlib
import json
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.domain import Language, ReviewStatus, StructuredCase

__all__ = [
    "ClinicalDomain",
    "EvidenceCategory",
    "FreshnessStatus",
    "EvidenceSufficiency",
    "AbstentionReason",
    "EvidenceSource",
    "FreshnessMetadata",
    "FreshnessPolicy",
    "EvidenceMetadata",
    "ClinicalChunk",
    "ClinicalDocument",
    "EvidenceCitation",
    "EvidenceItem",
    "EvidencePack",
    "RetrievalContext",
    "compute_document_hash",
    "compute_chunk_hash",
    "IngestionMethod",
    "AuthoritativeSourceMetadata",
    "IngestionMetadata",
    "SourceManifest",
]


class IngestionMethod(str, Enum):
    """Method utilized to acquire and ingest authoritative clinical source materials."""
    CURATED_SNAPSHOT = "curated_snapshot"
    STRUCTURED_EXTRACT = "structured_extract"
    MANUAL_VERIFIED = "manual_verified"


class ClinicalDomain(str, Enum):
    """Standard clinical domain taxonomy labels for evidence routing.
    NOTE: These are structural labels only; no clinical assertions.
    """
    CARDIOLOGY = "cardiology"
    NEUROLOGY = "neurology"
    RESPIRATORY = "respiratory"
    GASTROINTESTINAL = "gastrointestinal"
    DERMATOLOGY = "dermatology"
    PEDIATRICS = "pediatrics"
    WOMENS_HEALTH = "womens_health"
    INFECTIOUS_DISEASE = "infectious_disease"
    MEDICATIONS = "medications"
    DIAGNOSTICS_LABORATORY = "diagnostics_laboratory"
    FIRST_AID = "first_aid"
    PREVENTIVE_CARE = "preventive_care"
    NUTRITION = "nutrition"
    PUBLIC_HEALTH = "public_health"
    GENERAL = "general"
    OTHER = "other"


class EvidenceCategory(str, Enum):
    """Tier of clinical evidence curation."""
    CLINICAL_GUIDELINE = "clinical_guideline"
    PUBLIC_HEALTH_ADVISORY = "public_health_advisory"
    SYSTEMATIC_REVIEW = "systematic_review"
    CONSENSUS_STATEMENT = "consensus_statement"
    MONOGRAPH = "monograph"
    TRIAGE_PROTOCOL = "triage_protocol"
    EDUCATIONAL_REFERENCE = "educational_reference"


class FreshnessStatus(str, Enum):
    """Temporal currency of an evidence item under configured freshness policy."""
    CURRENT = "current"
    DUE_FOR_REVIEW = "due_for_review"
    STALE = "stale"
    UNAVAILABLE = "unavailable"


class EvidenceSufficiency(str, Enum):
    """Evidence coverage state for a query/case.
    Represents semantic coverage, NOT a clinical accuracy percentage.
    """
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INSUFFICIENT = "insufficient"


class AbstentionReason(str, Enum):
    """Deterministic reasons for abstaining from providing evidence-grounded guidance."""
    NONE = "none"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    NO_APPROVED_EVIDENCE = "no_approved_evidence"
    STALE_EVIDENCE = "stale_evidence"
    MISSING_PROVENANCE = "missing_provenance"
    UNSUPPORTED_DOMAIN = "unsupported_domain"
    LANGUAGE_MISMATCH = "language_mismatch"
    INTEGRITY_MISMATCH = "integrity_mismatch"
    MISSING_CONTEXT = "missing_context"


class EvidenceSource(BaseModel):
    """Authoritative publisher and provenance reference."""
    model_config = ConfigDict(frozen=True)

    name: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    url: str | None = None
    provenance_type: str = Field(default="authoritative_public_source", min_length=1)


class FreshnessMetadata(BaseModel):
    """Tracks publication, review, and expiry milestones without hardcoding clinical intervals."""
    model_config = ConfigDict(frozen=True)

    publication_date: date | None = None
    last_reviewed: date | None = None
    next_review: date | None = None
    review_interval_days: int | None = Field(default=None, gt=0)


class FreshnessPolicy(BaseModel):
    """Configurable freshness evaluation rules without universal clinical expiry assumptions.

    CRITICAL ARCHITECTURE PRINCIPLE:
    Medical knowledge documents do NOT universally expire after an arbitrary
    fixed period (such as 365 days). Clinical validity is determined through:
      1. Explicit document review metadata (explicit next_review date or source review interval).
      2. Configurable domain / jurisdiction policies explicitly established by clinical governance.
      3. Explicit CURRENT / DUE_FOR_REVIEW / STALE / UNAVAILABLE states.

    Without explicit next_review dates, source review intervals, or configured policy intervals,
    reviewed documents remain CURRENT. No universal clinical expiry interval is assumed.
    """
    model_config = ConfigDict(frozen=True)

    enforce_next_review: bool = True
    grace_period_days: int = Field(default=30, ge=0)
    domain_review_intervals: dict[ClinicalDomain, int] = Field(default_factory=dict)
    jurisdiction_review_intervals: dict[str, int] = Field(default_factory=dict)
    max_age_days: int | None = Field(default=None, gt=0)

    def evaluate(
        self,
        meta: FreshnessMetadata,
        domain: ClinicalDomain | None = None,
        jurisdiction: str | None = None,
        eval_date: date | None = None,
    ) -> FreshnessStatus:
        as_of = eval_date or date.today()

        # 0. If no review timestamp is recorded, freshness cannot be verified
        if meta.last_reviewed is None:
            return FreshnessStatus.UNAVAILABLE

        # 1. Explicit document review metadata: next_review milestone
        if meta.next_review and self.enforce_next_review:
            days_overdue = (as_of - meta.next_review).days
            if days_overdue > self.grace_period_days:
                return FreshnessStatus.STALE
            if days_overdue > 0:
                return FreshnessStatus.DUE_FOR_REVIEW
            return FreshnessStatus.CURRENT

        # 2. Explicit review interval attached to source/document metadata
        if meta.review_interval_days and self.enforce_next_review:
            effective_next_review = meta.last_reviewed + timedelta(days=meta.review_interval_days)
            days_overdue = (as_of - effective_next_review).days
            if days_overdue > self.grace_period_days:
                return FreshnessStatus.STALE
            if days_overdue > 0:
                return FreshnessStatus.DUE_FOR_REVIEW
            return FreshnessStatus.CURRENT

        # 3. Configured domain or jurisdiction policy review intervals (if any)
        configured_interval: int | None = None
        if domain and domain in self.domain_review_intervals:
            configured_interval = self.domain_review_intervals[domain]
        elif jurisdiction and jurisdiction in self.jurisdiction_review_intervals:
            configured_interval = self.jurisdiction_review_intervals[jurisdiction]
        elif self.max_age_days is not None:
            configured_interval = self.max_age_days

        if configured_interval is not None:
            days_since_review = (as_of - meta.last_reviewed).days
            if days_since_review > (configured_interval + self.grace_period_days):
                return FreshnessStatus.STALE
            if days_since_review > configured_interval:
                return FreshnessStatus.DUE_FOR_REVIEW
            return FreshnessStatus.CURRENT

        # 4. No universal clinical expiry: reviewed document remains CURRENT
        return FreshnessStatus.CURRENT


class EvidenceMetadata(BaseModel):
    """Contextual classification for clinical routing and governance."""
    model_config = ConfigDict(frozen=True)

    domain: ClinicalDomain = ClinicalDomain.GENERAL
    category: EvidenceCategory = EvidenceCategory.PUBLIC_HEALTH_ADVISORY
    language: Language = Language.EN
    jurisdiction: str = Field(default="global", min_length=1)
    clinical_scope: str = Field(default="general", min_length=1)
    target_audience: str = Field(default="patient", min_length=1)
    tags: list[str] = Field(default_factory=list)


def compute_chunk_hash(
    document_id: str,
    chunk_index: int,
    content: str,
    language: Language,
    version: str,
) -> str:
    """Deterministic hash for a chunk."""
    payload = {
        "chunk_index": chunk_index,
        "content": content,
        "document_id": document_id,
        "language": language.value,
        "version": version,
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ClinicalChunk(BaseModel):
    """A granular, citation-traceable fragment of a ClinicalDocument."""
    id: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    total_chunks: int = Field(ge=1)
    content: str = Field(min_length=1)
    terms: list[str] = Field(default_factory=list)
    start_char: int | None = Field(default=None, ge=0)
    end_char: int | None = Field(default=None, ge=0)
    content_hash: str = Field(min_length=1)
    metadata: EvidenceMetadata = Field(default_factory=EvidenceMetadata)


def compute_document_hash(
    doc_id: str,
    title: str,
    source: EvidenceSource,
    freshness: FreshnessMetadata,
    metadata: EvidenceMetadata,
    version: str,
    raw_content: str,
) -> str:
    """Canonical SHA-256 hash for document content and provenance."""
    payload = {
        "id": doc_id,
        "language": metadata.language.value,
        "last_reviewed": (
            freshness.last_reviewed.isoformat() if freshness.last_reviewed else None
        ),
        "metadata_domain": metadata.domain.value,
        "publication_date": (
            freshness.publication_date.isoformat() if freshness.publication_date else None
        ),
        "publisher": source.publisher,
        "raw_content": raw_content,
        "source_name": source.name,
        "title": title,
        "version": version,
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class ClinicalDocument(BaseModel):
    """Authoritative, governed clinical document."""
    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source: EvidenceSource
    freshness: FreshnessMetadata
    metadata: EvidenceMetadata = Field(default_factory=EvidenceMetadata)
    version: str = Field(default="1.0", min_length=1)
    raw_content: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    review_status: ReviewStatus = ReviewStatus.DRAFT

    # Human Clinical Review Governance (mandatory for APPROVED)
    reviewer_role: str = Field(default="QUALIFIED_CLINICAL_REVIEWER", min_length=1)
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    approval_metadata: dict[str, Any] = Field(default_factory=dict)

    # Version lineage & immutability tracking (Phase 30C)
    previous_document_id: str | None = None
    supersedes: str | None = None

    chunks: list[ClinicalChunk] = Field(default_factory=list)

    @model_validator(mode="after")
    def _verify_document_integrity(self) -> "ClinicalDocument":
        expected = compute_document_hash(
            doc_id=self.id,
            title=self.title,
            source=self.source,
            freshness=self.freshness,
            metadata=self.metadata,
            version=self.version,
            raw_content=self.raw_content,
        )
        if self.content_hash != expected:
            raise ValueError(
                f"Document integrity failure for '{self.id}': expected {expected}, got {self.content_hash}"
            )
        return self


class EvidenceCitation(BaseModel):
    """Traceable citation anchoring a generated statement to source evidence."""
    model_config = ConfigDict(frozen=True)

    source: str = Field(min_length=1)
    publisher: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    chunk_id: str | None = None
    version: str = Field(min_length=1)
    publication_date: date | None = None
    date_reviewed: date | None = None
    excerpt: str = ""
    url: str | None = None
    language: Language = Language.EN
    provenance: str = Field(min_length=1)


class EvidenceItem(BaseModel):
    """A scored, verified chunk paired with its provenance for downstream synthesis."""
    document_id: str = Field(min_length=1)
    chunk: ClinicalChunk
    source: EvidenceSource
    relevance_score: float = Field(ge=0.0, le=1.0, default=1.0)
    freshness_status: FreshnessStatus = FreshnessStatus.CURRENT
    citation: EvidenceCitation


class RetrievalContext(BaseModel):
    """Query context and constraints passed to the clinical retriever."""
    language: Language = Language.EN
    domain: ClinicalDomain | None = None
    min_sufficiency: EvidenceSufficiency = EvidenceSufficiency.LOW
    freshness_policy: FreshnessPolicy = Field(default_factory=FreshnessPolicy)
    allow_unreviewed: bool = False  # NEVER True in production
    evaluation_date: date | None = None


class EvidencePack(BaseModel):
    """Structured container of retrieved, verified evidence returned to orchestrator."""
    query: str
    items: list[EvidenceItem] = Field(default_factory=list)
    citations: list[EvidenceCitation] = Field(default_factory=list)
    sufficiency: EvidenceSufficiency = EvidenceSufficiency.INSUFFICIENT
    should_abstain: bool = True
    abstention_reason: AbstentionReason = AbstentionReason.INSUFFICIENT_EVIDENCE
    retrieval_metadata: dict[str, Any] = Field(default_factory=dict)
    limitations: list[str] = Field(default_factory=list)
    evaluated_at: datetime


class AuthoritativeSourceMetadata(BaseModel):
    """Metadata originating directly from the authoritative clinical publisher/source.

    Strictly captures publisher-verified attributes without synthetic expansion.
    """
    model_config = ConfigDict(frozen=True)

    publisher: str = Field(min_length=1)
    title: str = Field(min_length=1)
    canonical_url: str = Field(min_length=1)
    official_publication_date: date | None = None
    official_update_date: date | None = None
    official_version: str | None = None  # None if publisher does not assign clinical versions
    jurisdiction: str = Field(default="global", min_length=1)
    language: Language = Language.EN
    clinical_domain: ClinicalDomain = ClinicalDomain.NEUROLOGY


class IngestionMetadata(BaseModel):
    """Internal pipeline metadata recorded during SehatAI evidence ingestion.

    Distinguishes SehatAI internal processing artifacts from authoritative source metadata.
    """
    model_config = ConfigDict(frozen=True)

    ingestion_id: str = Field(min_length=1)
    retrieved_at: datetime
    ingestion_method: IngestionMethod = IngestionMethod.CURATED_SNAPSHOT
    raw_content_sha256: str = Field(min_length=1)
    internal_version: str = Field(default="1.0", min_length=1)
    provenance_type: str = Field(default="authoritative_public_source", min_length=1)
    verification_status: str = Field(
        default="source snapshot awaiting authoritative retrieval verification"
    )
    previous_snapshot_id: str | None = None
    supersedes: str | None = None


class SourceManifest(BaseModel):
    """Machine-readable provenance manifest for an authoritative clinical evidence source.

    STRICT GOVERNANCE ISOLATION (Phase 30B-H):
    Explicitly distinguishes external AUTHORITATIVE SOURCE METADATA from internal
    INGESTION METADATA. Internal pipeline versions (e.g. 1.0) are never conflated with
    official source release numbers.
    """
    model_config = ConfigDict(frozen=True)

    source: AuthoritativeSourceMetadata
    ingestion: IngestionMetadata
    document_id: str = Field(min_length=1)
    content_hash: str = Field(min_length=1)
    review_status: ReviewStatus = ReviewStatus.PENDING_DOMAIN_REVIEW
    chunks_count: int = Field(ge=1)

    @model_validator(mode="before")
    @classmethod
    def _migrate_flat_manifest(cls, data: Any) -> Any:
        if isinstance(data, dict) and "source" not in data and "publisher" in data:
            source_data = {
                "publisher": data.get("publisher"),
                "title": data.get("title"),
                "canonical_url": data.get("canonical_url"),
                "official_publication_date": data.get("official_publication_date") or data.get("publication_date"),
                "official_update_date": data.get("official_update_date"),
                "official_version": data.get("official_version") or (None if data.get("source_version") == "1.0" else data.get("source_version")),
                "jurisdiction": data.get("jurisdiction", "global"),
                "language": data.get("language", Language.EN),
                "clinical_domain": data.get("clinical_domain", ClinicalDomain.NEUROLOGY),
            }
            ingestion_data = {
                "ingestion_id": data.get("ingestion_id") or data.get("source_id", "unknown-ingestion"),
                "retrieved_at": data.get("retrieved_at"),
                "ingestion_method": data.get("ingestion_method", IngestionMethod.CURATED_SNAPSHOT),
                "raw_content_sha256": data.get("raw_content_sha256", ""),
                "internal_version": data.get("internal_version") or data.get("source_version") or "1.0",
                "provenance_type": data.get("provenance_type", "authoritative_public_source"),
                "verification_status": data.get(
                    "verification_status",
                    "source snapshot awaiting authoritative retrieval verification",
                ),
            }
            return {
                "source": source_data,
                "ingestion": ingestion_data,
                "document_id": data.get("document_id"),
                "content_hash": data.get("content_hash"),
                "review_status": data.get("review_status", ReviewStatus.PENDING_DOMAIN_REVIEW),
                "chunks_count": data.get("chunks_count", 1),
            }
        return data

    @property
    def source_id(self) -> str:
        return self.ingestion.ingestion_id

    @property
    def publisher(self) -> str:
        return self.source.publisher

    @property
    def title(self) -> str:
        return self.source.title

    @property
    def canonical_url(self) -> str:
        return self.source.canonical_url

    @property
    def publication_date(self) -> date | None:
        return self.source.official_publication_date

    @property
    def official_update_date(self) -> date | None:
        return self.source.official_update_date

    @property
    def retrieved_at(self) -> datetime:
        return self.ingestion.retrieved_at

    @property
    def source_version(self) -> str | None:
        return self.source.official_version

    @property
    def internal_version(self) -> str:
        return self.ingestion.internal_version

    @property
    def language(self) -> Language:
        return self.source.language

    @property
    def clinical_domain(self) -> ClinicalDomain:
        return self.source.clinical_domain

    @property
    def jurisdiction(self) -> str:
        return self.source.jurisdiction

    @property
    def provenance_type(self) -> str:
        return self.ingestion.provenance_type

    @property
    def ingestion_method(self) -> IngestionMethod:
        return self.ingestion.ingestion_method

    @property
    def raw_content_sha256(self) -> str:
        return self.ingestion.raw_content_sha256

    @property
    def verification_status(self) -> str:
        return self.ingestion.verification_status

    @property
    def previous_snapshot_id(self) -> str | None:
        return self.ingestion.previous_snapshot_id

    @property
    def supersedes(self) -> str | None:
        return self.ingestion.supersedes


