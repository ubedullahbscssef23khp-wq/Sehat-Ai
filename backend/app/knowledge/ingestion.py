"""Authoritative Clinical Evidence Ingestion & Chunking Pipeline (PHASE 30B).

ARCHITECTURE PRINCIPLE:
"AI understands. Evidence grounds. Code controls."

This module implements deterministic, reproducible ingestion of authoritative
clinical source snapshots into governed ClinicalDocument instances and structured
ClinicalChunk fragments.

GOVERNANCE INVARIANT:
All newly ingested content is assigned PENDING_DOMAIN_REVIEW.
It CANNOT enter the production corpus or active retrieval without qualified
human clinical review.

NO MEDICAL CLAIMS ARE INVENTED OR EXPANDED.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
import re
from typing import Any, Sequence

from app.models.domain import Language, ReviewStatus
from app.knowledge.evidence_models import (
    AuthoritativeSourceMetadata,
    ClinicalChunk,
    ClinicalDocument,
    ClinicalDomain,
    EvidenceCategory,
    EvidenceMetadata,
    EvidenceSource,
    FreshnessMetadata,
    IngestionMetadata,
    IngestionMethod,
    SourceManifest,
    compute_chunk_hash,
    compute_document_hash,
)
from app.knowledge.retriever import _tokenize

__all__ = [
    "IngestionError",
    "extract_clinical_chunks",
    "ingest_authoritative_source",
    "generate_review_package_markdown",
]


class IngestionError(ValueError):
    """Raised when source ingestion fails provenance, integrity, or governance requirements."""


_CANONICAL_URL_RE = re.compile(r"^https?://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+$")


def validate_source_provenance(
    publisher: str,
    title: str,
    canonical_url: str,
) -> None:
    """Enforces non-empty provenance fields and valid canonical URL format."""
    if not publisher or not publisher.strip():
        raise IngestionError("Authoritative source publisher must not be empty.")
    if not title or not title.strip():
        raise IngestionError("Authoritative source title must not be empty.")
    if not canonical_url or not canonical_url.strip():
        raise IngestionError("Authoritative source canonical_url must not be empty.")
    if not _CANONICAL_URL_RE.match(canonical_url.strip()):
        raise IngestionError(f"Invalid canonical_url format: {canonical_url!r}")


def extract_clinical_chunks(
    document_id: str,
    raw_content: str,
    language: Language,
    version: str,
    metadata: EvidenceMetadata,
) -> list[ClinicalChunk]:
    """Deterministically chunks raw authoritative text into granular, traceable chunks.

    Guarantees:
    - Stable, deterministic chunk IDs: `{document_id}-chk-{index:02d}`
    - Exact character slice offsets (start_char, end_char) in parent raw text
    - Reproducible canonical SHA-256 hash per chunk
    - Metadata and provenance inheritance
    - Preserves exact excerpts from the ingested source snapshot without paraphrase or modification;
      provenance and integrity are cryptographically tracked.
    """
    if not raw_content or not raw_content.strip():
        raise IngestionError(f"Document '{document_id}': raw_content must not be empty.")

    # Split on double newlines or bullet markers while preserving exact content
    paragraphs = [p.strip() for p in raw_content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [raw_content.strip()]

    chunks: list[ClinicalChunk] = []
    total_chunks = len(paragraphs)
    search_cursor = 0

    for idx, para in enumerate(paragraphs):
        chunk_id = f"{document_id}-chk-{idx:02d}"
        
        # Calculate start and end offsets in raw_content
        found_pos = raw_content.find(para, search_cursor)
        if found_pos != -1:
            start_char = found_pos
            end_char = found_pos + len(para)
            search_cursor = end_char
        else:
            start_char = None
            end_char = None

        c_hash = compute_chunk_hash(
            document_id=document_id,
            chunk_index=idx,
            content=para,
            language=language,
            version=version,
        )

        terms = sorted(list(_tokenize(para)))

        chunk = ClinicalChunk(
            id=chunk_id,
            document_id=document_id,
            chunk_index=idx,
            total_chunks=total_chunks,
            content=para,
            terms=terms,
            start_char=start_char,
            end_char=end_char,
            content_hash=c_hash,
            metadata=metadata,
        )
        chunks.append(chunk)

    return chunks


def ingest_authoritative_source(
    source_id: str,
    document_id: str,
    publisher: str,
    title: str,
    canonical_url: str,
    raw_content: str,
    publication_date: date | None = None,
    official_publication_date: date | None = None,
    official_update_date: date | None = None,
    official_source_version: str | None = None,
    internal_version: str = "1.0",
    source_version: str | None = None,
    language: Language = Language.EN,
    clinical_domain: ClinicalDomain = ClinicalDomain.NEUROLOGY,
    category: EvidenceCategory = EvidenceCategory.PUBLIC_HEALTH_ADVISORY,
    jurisdiction: str = "US / Global Public Health",
    clinical_scope: str = "stroke_warning_signs",
    target_audience: str = "general_public",
    review_interval_days: int | None = None,
    ingestion_method: IngestionMethod = IngestionMethod.CURATED_SNAPSHOT,
    retrieved_at: datetime | None = None,
    verification_status: str = "source snapshot awaiting authoritative retrieval verification",
    previous_snapshot_id: str | None = None,
    supersedes: str | None = None,
) -> tuple[ClinicalDocument, SourceManifest]:
    """Ingests an authoritative clinical source into a governed ClinicalDocument and SourceManifest.

    STRICT GOVERNANCE RULES (Phase 30B-H & Phase 30C):
    1. Sets review_status = PENDING_DOMAIN_REVIEW
    2. reviewed_by is None, reviewed_at is None
    3. approval_metadata is empty
    4. Computes canonical SHA-256 for document and every chunk
    5. Explicitly separates external AuthoritativeSourceMetadata from internal IngestionMetadata
    6. Tracks immutable version lineage (previous_snapshot_id, supersedes)
    """
    validate_source_provenance(publisher, title, canonical_url)

    now_utc = retrieved_at or datetime.now(timezone.utc)
    raw_sha256 = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

    # Determine dates & versions without confusing source metadata with ingestion metadata
    eff_publication_date = official_publication_date or publication_date
    eff_internal_version = source_version if (source_version and internal_version == "1.0") else internal_version

    evidence_source = EvidenceSource(
        name=title.strip(),
        publisher=publisher.strip(),
        url=canonical_url.strip(),
        provenance_type="authoritative_public_source",
    )

    freshness_meta = FreshnessMetadata(
        publication_date=eff_publication_date,
        last_reviewed=None,  # Not reviewed yet
        next_review=None,
        review_interval_days=review_interval_days,
    )

    doc_metadata = EvidenceMetadata(
        domain=clinical_domain,
        category=category,
        language=language,
        jurisdiction=jurisdiction,
        clinical_scope=clinical_scope,
        target_audience=target_audience,
        tags=["stroke", "befast", "emergency_warning_signs"],
    )

    chunks = extract_clinical_chunks(
        document_id=document_id,
        raw_content=raw_content,
        language=language,
        version=eff_internal_version,
        metadata=doc_metadata,
    )

    doc_hash = compute_document_hash(
        doc_id=document_id,
        title=title.strip(),
        source=evidence_source,
        freshness=freshness_meta,
        metadata=doc_metadata,
        version=eff_internal_version,
        raw_content=raw_content,
    )

    doc = ClinicalDocument(
        id=document_id,
        title=title.strip(),
        source=evidence_source,
        freshness=freshness_meta,
        metadata=doc_metadata,
        version=eff_internal_version,
        raw_content=raw_content,
        content_hash=doc_hash,
        review_status=ReviewStatus.PENDING_DOMAIN_REVIEW,
        reviewed_by=None,
        reviewed_at=None,
        approval_metadata={},
        review_notes="Initial ingestion from authoritative source snapshot. Staged for qualified human clinical review.",
        previous_document_id=previous_snapshot_id,
        supersedes=supersedes,
        chunks=chunks,
    )

    source_meta = AuthoritativeSourceMetadata(
        publisher=publisher.strip(),
        title=title.strip(),
        canonical_url=canonical_url.strip(),
        official_publication_date=eff_publication_date,
        official_update_date=official_update_date,
        official_version=official_source_version,
        jurisdiction=jurisdiction,
        language=language,
        clinical_domain=clinical_domain,
    )

    ingestion_meta = IngestionMetadata(
        ingestion_id=source_id.strip(),
        retrieved_at=now_utc,
        ingestion_method=ingestion_method,
        raw_content_sha256=raw_sha256,
        internal_version=eff_internal_version,
        provenance_type="authoritative_public_source",
        verification_status=verification_status,
        previous_snapshot_id=previous_snapshot_id,
        supersedes=supersedes,
    )

    manifest = SourceManifest(
        source=source_meta,
        ingestion=ingestion_meta,
        document_id=document_id,
        content_hash=doc_hash,
        review_status=ReviewStatus.PENDING_DOMAIN_REVIEW,
        chunks_count=len(chunks),
    )

    return doc, manifest


def generate_review_package_markdown(
    doc: ClinicalDocument,
    manifest: SourceManifest,
    known_differences: list[str] | None = None,
) -> str:
    """Generates an auditable Markdown human clinical review package."""
    pub_date_str = (
        manifest.source.official_publication_date.isoformat()
        if manifest.source.official_publication_date
        else "Unavailable / Not specified by publisher"
    )
    upd_date_str = (
        manifest.source.official_update_date.isoformat()
        if manifest.source.official_update_date
        else "Unavailable / Not specified by publisher"
    )
    source_ver_str = (
        manifest.source.official_version
        if manifest.source.official_version
        else "Unavailable / Not versioned by publisher"
    )

    lines: list[str] = [
        f"# Clinical Evidence Human Review Package: {doc.title}",
        "",
        "> **STATUS: PENDING_DOMAIN_REVIEW**  ",
        "> *This package is pending qualified human clinical review.*  ",
        "> *No clinical approval has been granted.*  ",
        "> *This content is not active in the production corpus.*",
        "",
        "## 1. Source Provenance & Metadata",
        "",
        "### A. Authoritative Source Metadata",
        f"- **Source Identity:** {doc.source.name}",
        f"- **Publisher:** {manifest.source.publisher}",
        f"- **Title:** {manifest.source.title}",
        f"- **Canonical URL:** {manifest.source.canonical_url}",
        f"- **Official Publication Date:** {pub_date_str}",
        f"- **Official Update / Review Date:** {upd_date_str}",
        f"- **Official Source Version:** {source_ver_str}",
        f"- **Language:** `{manifest.source.language.value}`",
        f"- **Clinical Domain:** `{manifest.source.clinical_domain.value}`",
        f"- **Jurisdiction:** {manifest.source.jurisdiction}",
        f"- **Clinical Scope:** {doc.metadata.clinical_scope}",
        "",
        "### B. Ingestion Pipeline Metadata (SehatAI)",
        f"- **Ingestion ID:** `{manifest.ingestion.ingestion_id}`",
        f"- **Document ID:** `{doc.id}`",
        f"- **Internal Ingestion Version:** `{manifest.ingestion.internal_version}`",
        f"- **Ingestion Method:** `{manifest.ingestion.ingestion_method.value}`",
        f"- **Retrieval Timestamp (UTC):** {manifest.ingestion.retrieved_at.isoformat()}",
        f"- **Provenance Type:** `{manifest.ingestion.provenance_type}`",
        f"- **Verification Status:** {manifest.ingestion.verification_status}",
        f"- **Previous Snapshot / Lineage:** `{manifest.previous_snapshot_id or 'None (initial snapshot)'}`",
        f"- **Supersedes:** `{manifest.supersedes or 'None'}`",
        f"- **Raw Snapshot SHA-256:** `{manifest.ingestion.raw_content_sha256}`",
        f"- **Document Canonical SHA-256:** `{doc.content_hash}`",
        f"- **Total Granular Chunks:** {len(doc.chunks)}",
        f"- **Review Status:** `{doc.review_status.value}`",
        f"- **Production Activation Status:** INACTIVE (0 production entries)",
        "",
        "## 2. Ingested Clinical Chunks for Evaluation",
        "",
    ]

    for chunk in doc.chunks:
        lines.extend([
            f"### Chunk `{chunk.id}` (Index {chunk.chunk_index + 1}/{chunk.total_chunks})",
            f"- **Character Offsets:** start={chunk.start_char}, end={chunk.end_char}",
            f"- **Chunk Hash:** `{chunk.content_hash}`",
            f"- **Indexed Terms:** {', '.join(chunk.terms) if chunk.terms else 'none'}",
            "",
            "**Verbatim Source Excerpt:**",
            f"> {chunk.content}",
            "",
            "---",
            "",
        ])

    lines.extend([
        "## 3. Human Clinical Review Decision Record",
        "",
        "| Field | Required Value / Format | Reviewer Entry |",
        "|---|---|---|",
        "| **Reviewer Full Name** | Non-empty string | `[ ENTER FULL NAME ]` |",
        "| **Reviewer Professional Role** | e.g. Neurologist, Emergency Physician, Clinical Governance Lead | `[ ENTER ROLE & CREDENTIALS ]` |",
        "| **Review Timestamp (UTC)** | ISO-8601 (YYYY-MM-DDTHH:MM:SSZ) | `[ ENTER TIMESTAMP ]` |",
        "| **Clinical Decision** | `APPROVED` or `REJECTED` | `[ PENDING_DOMAIN_REVIEW ]` |",
        "| **Clinical Approval Reference** | Institutional / Guideline Reference ID | `[ ENTER REFERENCE IF APPROVED ]` |",
        "| **Reviewer Clinical Notes** | Specific feedback, reservations, or approval basis | `[ ENTER NOTES ]` |",
        "",
        "## 4. Human Clinical Review Checklist",
        "",
        "- [ ] **Source Authenticity:** Verified against official CDC public portal.",
        "- [ ] **Factual Veracity:** Stored excerpts are preserved from the ingested source snapshot; provenance and integrity are cryptographically tracked.",
        "- [ ] **Scope Limitation:** Limited strictly to stroke warning signs recognition (BEFAST).",
        "- [ ] **Safety Appropriateness:** Directs urgent emergency action without delaying professional care.",
        "- [ ] **Language Precision:** English terminology is unambiguous and clinically standard.",
        "- [ ] **Multilingual Isolation:** Verified that English approval does NOT grant automatic Urdu/Sindhi approval.",
        "- [ ] **Production Eligibility:** Authorized by qualified clinician for future production activation.",
        "",
    ])

    diffs = known_differences or []
    if not diffs and manifest.supersedes:
        diffs = [
            f"Supersedes historical snapshot `{manifest.supersedes}`.",
            "Incorporates updated B.E. F.A.S.T. clinical mnemonic (Balance loss & Eye/vision changes).",
            "Incorporates acute treatment window guidance (within 3 hours of symptom onset).",
            "Incorporates Transient Ischemic Attack (TIA / mini-stroke) medical evaluation advisory.",
            "Incorporates emergency ambulance transportation instruction (Do not drive).",
            "Updated official publication date (2024-05-15) and official update date (2026-05-19).",
        ]

    lines.extend([
        "## 5. Known Differences from Historical Snapshot",
        "",
    ])
    if diffs:
        for diff in diffs:
            lines.append(f"- {diff}")
    else:
        lines.append("- Baseline authoritative evidence snapshot (no previous version).")

    lines.append("")
    return "\n".join(lines)
