"""Phase 30C: Governed Re-Ingestion of Verified CDC Stroke Source.

Validates the creation of a new immutable CDC snapshot (cdc-stroke-signs-2026)
while preserving the historical baseline (cdc-stroke-signs-2024).

ARCHITECTURAL PRINCIPLE:
"AI understands. Evidence grounds. Code controls."

GOVERNANCE INVARIANTS:
1. Historical snapshot (cdc-stroke-signs-2024) remains immutable and unchanged.
2. Current snapshot (cdc-stroke-signs-2026) is created separately with full lineage.
3. Review status remains PENDING_DOMAIN_REVIEW with no fake sign-offs.
4. Production knowledge corpus remains strictly 0 entries.
5. Production clinical retriever excludes all unreviewed/pending evidence.
6. Zero overclaiming ("zero hallucination", "guaranteed accurate") is permitted.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
import json
from pathlib import Path
import pytest

from app.models.domain import Language, ReviewStatus
from app.knowledge.evidence_models import (
    AbstentionReason,
    AuthoritativeSourceMetadata,
    ClinicalChunk,
    ClinicalDocument,
    ClinicalDomain,
    EvidenceCategory,
    EvidenceCitation,
    EvidenceItem,
    EvidenceMetadata,
    EvidencePack,
    EvidenceSource,
    EvidenceSufficiency,
    FreshnessMetadata,
    FreshnessPolicy,
    FreshnessStatus,
    IngestionMetadata,
    IngestionMethod,
    RetrievalContext,
    SourceManifest,
    compute_chunk_hash,
    compute_document_hash,
)
from app.knowledge.governance import (
    GovernanceError,
    promote_to_approved,
    validate_for_approval,
    validate_production_eligibility,
)
from app.knowledge.ingestion import (
    IngestionError,
    extract_clinical_chunks,
    generate_review_package_markdown,
    ingest_authoritative_source,
    validate_source_provenance,
)
from app.knowledge.paths import CONTENT_DIR
from app.knowledge.loader import load_entries_dir
from app.knowledge.retriever import LexicalClinicalRetriever

SAMPLE_CDC_2024_TEXT = (
    "Signs and symptoms of stroke: During a stroke, every minute counts! "
    "Fast treatment can lessen the brain damage that stroke can cause. "
    "By knowing the signs and symptoms of stroke, you can take quick action and perhaps save a life.\n\n"
    "Signs of stroke in men and women include: Sudden numbness or weakness in the face, "
    "arm, or leg, especially on one side of the body.\n\n"
    "Sudden confusion, trouble speaking, or difficulty understanding speech.\n\n"
    "Sudden trouble seeing in one or both eyes.\n\n"
    "Sudden trouble walking, dizziness, loss of balance, or lack of coordination.\n\n"
    "Sudden severe headache with no known cause.\n\n"
    "Call 9-1-1 right away if you or someone else has any of these symptoms. Act F.A.S.T. to identify stroke signs: "
    "Face drooping (ask the person to smile), Arm weakness (ask the person to raise both arms), "
    "Speech difficulty (ask the person to repeat a simple phrase), and Time to call 9-1-1."
)

VERIFIED_CDC_2026_TEXT = (
    "Key points: During a stroke, every minute counts. Fast treatment can lessen the brain damage that stroke can cause.\n\n"
    "Signs and symptoms: By knowing the signs and symptoms of stroke, you can take quick action and perhaps save a life—maybe even your own.\n\n"
    "Signs of stroke in men and women include: Sudden trouble walking, dizziness, loss of balance, or lack of coordination.\n\n"
    "Sudden trouble seeing.\n\n"
    "Sudden numbness or weakness in the face, arm, or leg, especially on one side of the body.\n\n"
    "Sudden confusion, trouble speaking, or difficulty understanding speech.\n\n"
    "Sudden severe headache with no known cause.\n\n"
    "Call 9-1-1 right away if you or someone else has any of these symptoms.\n\n"
    "When to seek emergency help: B.E. F.A.S.T. to help stroke patients get the treatments they need. "
    "The stroke treatments that work best are available only if the stroke is recognized and diagnosed within 3 hours of the first symptoms. "
    "Stroke patients may not be eligible for these treatments if they don't arrive at the hospital in time.\n\n"
    "If you think someone may be having a stroke, B.E. F.A.S.T. and do the following test:\n"
    "B—Balance Loss: Ask the person if they are feeling off-balance or dizzy.\n"
    "E—Eye (Vision) Changes: Ask the person if they have trouble seeing normally.\n"
    "F—Face: Ask the person to smile. Does one side of the face droop?\n"
    "A—Arms: Ask the person to raise both arms. Does one arm drift downward?\n"
    "S—Speech: Ask the person to repeat a simple phrase. Is the speech slurred or strange?\n"
    "T—Time: If you see any of these signs, call 9-1-1 right away.\n\n"
    "Note the time when any symptoms first appear. This information helps health care providers determine the best treatment. "
    "Do not drive to the hospital or let someone else drive you. Call 9-1-1 for an ambulance so that medical personnel can begin life-saving treatment on the way to the emergency room.\n\n"
    "What should I do to treat a transient ischemic attack (\"mini-stroke\")? If your stroke symptoms go away after a few minutes, "
    "you may have had a transient ischemic attack (TIA), also sometimes called a \"mini-stroke.\" "
    "Although brief, a TIA is a sign of a serious condition that will not go away without medical help.\n\n"
    "Unfortunately, because TIAs clear up, many people ignore them. But paying attention to a TIA can save your life. "
    "If you think you or someone you know has had a TIA, tell a health care team about the symptoms right away."
)


# A. New snapshot is created separately from old snapshot
def test_new_snapshot_created_separately_from_old_snapshot():
    doc_old, manifest_old = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_2024_TEXT,
        official_publication_date=date(2024, 5, 1),
        internal_version="1.0",
    )
    doc_new, manifest_new = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
        official_source_version=None,
        internal_version="2.0",
        previous_snapshot_id="cdc-stroke-signs-2024",
        supersedes="cdc-stroke-signs-2024",
    )
    assert doc_old.id == "cdc-stroke-signs-2024"
    assert doc_new.id == "cdc-stroke-signs-2026"
    assert doc_old.id != doc_new.id
    assert doc_old.content_hash != doc_new.content_hash
    assert manifest_old.source_id != manifest_new.source_id
    assert len(doc_old.chunks) == 7
    assert len(doc_new.chunks) == 13


# B. Old snapshot is not modified and remains immutable
def test_old_snapshot_is_not_modified():
    doc_old, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_2024_TEXT,
        publication_date=date(2024, 5, 1),
        internal_version="1.0",
    )
    # The historical content hash must remain exact
    assert doc_old.content_hash == "698a1bf2d971f43b67fa5e918dfb42f1bebafa8abb3cd12b1d6cbd86313f253e"

    # Verify historical manifest file exists and remains intact
    hist_manifest_path = Path(__file__).resolve().parent.parent / "app" / "knowledge" / "manifests" / "cdc_stroke_signs_manifest.json"
    assert hist_manifest_path.exists()
    with open(hist_manifest_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["document_id"] == "cdc-stroke-signs-2024"
    assert data["content_hash"] == "698a1bf2d971f43b67fa5e918dfb42f1bebafa8abb3cd12b1d6cbd86313f253e"
    assert data["chunks_count"] == 7


# C. New snapshot has deterministic hashes
def test_new_snapshot_has_deterministic_hashes():
    doc1, manifest1 = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
        official_source_version=None,
        internal_version="2.0",
        previous_snapshot_id="cdc-stroke-signs-2024",
        supersedes="cdc-stroke-signs-2024",
    )
    doc2, manifest2 = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
        official_source_version=None,
        internal_version="2.0",
        previous_snapshot_id="cdc-stroke-signs-2024",
        supersedes="cdc-stroke-signs-2024",
    )
    assert doc1.content_hash == doc2.content_hash
    assert manifest1.content_hash == manifest2.content_hash
    assert doc1.content_hash == "8c24edf1467aa59b38d01b97fe907d9edd1c0bbd051ae67caaf9a651e59f50b4"
    assert [c.content_hash for c in doc1.chunks] == [c.content_hash for c in doc2.chunks]


# D. Official source metadata is separated from internal ingestion metadata
def test_official_source_metadata_separated_from_internal_ingestion_metadata():
    _, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
        official_source_version=None,
        internal_version="2.0",
        previous_snapshot_id="cdc-stroke-signs-2024",
        supersedes="cdc-stroke-signs-2024",
    )
    # Source metadata (publisher-verified facts)
    assert isinstance(manifest.source, AuthoritativeSourceMetadata)
    assert manifest.source.publisher == "Centers for Disease Control and Prevention"
    assert manifest.source.title == "Signs and Symptoms of Stroke"
    assert manifest.source.canonical_url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert manifest.source.official_publication_date == date(2024, 5, 15)
    assert manifest.source.official_update_date == date(2026, 5, 19)

    # Ingestion metadata (internal pipeline facts)
    assert isinstance(manifest.ingestion, IngestionMetadata)
    assert manifest.ingestion.ingestion_id == "src-cdc-stroke-signs-2026-v1"
    assert manifest.ingestion.internal_version == "2.0"
    assert manifest.ingestion.previous_snapshot_id == "cdc-stroke-signs-2024"
    assert manifest.ingestion.supersedes == "cdc-stroke-signs-2024"


# E. Official CDC version remains None if unavailable
def test_official_cdc_version_remains_none_if_unavailable():
    _, manifest = ingest_authoritative_source(
        source_id="src-cdc-2026",
        document_id="cdc-2026",
        publisher="CDC",
        title="Stroke",
        canonical_url="https://www.cdc.gov/stroke",
        raw_content="Stroke content.",
        official_source_version=None,
        internal_version="2.0",
    )
    assert manifest.source.official_version is None
    assert manifest.source_version is None
    assert manifest.ingestion.internal_version == "2.0"
    assert manifest.internal_version == "2.0"


# F, G, H, I. Review lifecycle: PENDING_DOMAIN_REVIEW and empty sign-off
def test_new_snapshot_review_lifecycle_pending_and_empty_signoff():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
    )
    assert doc.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
    assert doc.reviewed_by is None
    assert doc.reviewed_at is None
    assert doc.approval_metadata == {}
    assert manifest.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW


# J. Production corpus remains empty
def test_production_corpus_remains_empty():
    entries = load_entries_dir(CONTENT_DIR)
    assert len(entries) == 0, "Production knowledge corpus must be 0 entries."


# K. Production retriever excludes pending content
def test_production_retriever_excludes_pending_content():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
    )
    retriever = LexicalClinicalRetriever([doc])

    # In production (allow_unreviewed=False), pending content is strictly excluded
    pack = retriever.retrieve("sudden balance loss eye vision changes", context=RetrievalContext(allow_unreviewed=False))
    assert pack.should_abstain is True
    assert len(pack.items) == 0
    assert pack.abstention_reason in (
        AbstentionReason.NO_APPROVED_EVIDENCE,
        AbstentionReason.INSUFFICIENT_EVIDENCE,
    )


# L. No fake approval is possible
def test_no_fake_approval_is_possible():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
    )
    # Cannot approve without valid reviewer identity
    with pytest.raises(GovernanceError):
        promote_to_approved(doc, reviewer_name="", approval_ref="REF")

    # Cannot approve without approval reference
    with pytest.raises(GovernanceError):
        promote_to_approved(doc, reviewer_name="Dr. Valid MD", approval_ref="")

    # Unapproved doc cannot pass production eligibility validation
    with pytest.raises(GovernanceError):
        validate_production_eligibility(doc)


# M. Historical snapshot remains retrievable for audit/history
def test_historical_snapshot_remains_retrievable_for_audit_history():
    hist_manifest_file = Path(__file__).resolve().parent.parent / "app" / "knowledge" / "manifests" / "cdc_stroke_signs_manifest.json"
    curr_manifest_file = Path(__file__).resolve().parent.parent / "app" / "knowledge" / "manifests" / "cdc_stroke_signs_2026_manifest.json"

    assert hist_manifest_file.exists()
    assert curr_manifest_file.exists()

    with open(hist_manifest_file, encoding="utf-8") as f:
        hist_data = json.load(f)
    with open(curr_manifest_file, encoding="utf-8") as f:
        curr_data = json.load(f)

    hist_manifest = SourceManifest.model_validate(hist_data)
    curr_manifest = SourceManifest.model_validate(curr_data)

    assert hist_manifest.document_id == "cdc-stroke-signs-2024"
    assert curr_manifest.document_id == "cdc-stroke-signs-2026"
    assert curr_manifest.previous_snapshot_id == "cdc-stroke-signs-2024"
    assert curr_manifest.supersedes == "cdc-stroke-signs-2024"


# N. New snapshot has correct provenance citations
def test_new_snapshot_has_correct_provenance():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
    )
    # In review mode fixture only
    approved_doc = promote_to_approved(doc, reviewer_name="Dr. Neurologist MD", approval_ref="REF-2026-TEST")
    retriever = LexicalClinicalRetriever([approved_doc])

    pack = retriever.retrieve("balance loss dizziness eye changes", context=RetrievalContext(allow_unreviewed=False))
    assert pack.should_abstain is False
    assert len(pack.citations) >= 1
    citation = pack.citations[0]
    assert citation.publisher == "Centers for Disease Control and Prevention"
    assert citation.url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert citation.document_id == "cdc-stroke-signs-2026"
    assert "cdc-stroke-signs-2026-chk-" in (citation.chunk_id or "")


# O. Chunk hashes are deterministic
def test_chunk_hashes_are_deterministic():
    chunks = extract_clinical_chunks(
        document_id="cdc-stroke-signs-2026",
        raw_content=VERIFIED_CDC_2026_TEXT,
        language=Language.EN,
        version="2.0",
        metadata=EvidenceMetadata(domain=ClinicalDomain.NEUROLOGY),
    )
    assert len(chunks) == 13
    for chunk in chunks:
        expected = compute_chunk_hash(
            document_id="cdc-stroke-signs-2026",
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            language=Language.EN,
            version="2.0",
        )
        assert chunk.content_hash == expected


# P. Changing source content changes the corresponding hash
def test_changing_source_content_changes_hash():
    doc_original, _ = ingest_authoritative_source(
        source_id="src-original",
        document_id="doc-original",
        publisher="CDC",
        title="Stroke Signs",
        canonical_url="https://www.cdc.gov/stroke",
        raw_content="Exact sentence from source.",
    )
    doc_mutated, _ = ingest_authoritative_source(
        source_id="src-original",
        document_id="doc-original",
        publisher="CDC",
        title="Stroke Signs",
        canonical_url="https://www.cdc.gov/stroke",
        raw_content="Exact sentence from source modified.",
    )
    assert doc_original.content_hash != doc_mutated.content_hash
    assert doc_original.chunks[0].content_hash != doc_mutated.chunks[0].content_hash


# Q. No "zero hallucination" / "guaranteed accurate" / equivalent overclaiming exists
def test_no_overclaiming_in_review_package():
    review_pkg_path = Path(__file__).resolve().parent.parent.parent / "docs" / "review_packages" / "CDC_STROKE_SIGNS_CURRENT_REVIEW.md"
    assert review_pkg_path.exists()
    content = review_pkg_path.read_text(encoding="utf-8")

    # Precise integrity phrasing required
    assert "Stored excerpts are preserved from the ingested source snapshot; provenance and integrity are cryptographically tracked." in content

    # Forbidden overclaiming terms
    lower_content = content.lower()
    assert "zero hallucination" not in lower_content
    assert "zero medical hallucination" not in lower_content
    assert "guaranteed accurate" not in lower_content
    assert "100% correct" not in lower_content


# R. No invented clinical content is introduced
def test_no_invented_clinical_content_is_introduced():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
    )
    for chunk in doc.chunks:
        # Every chunk content must be a direct substring of raw content
        assert chunk.content in VERIFIED_CDC_2026_TEXT


# S. No translation is introduced
def test_no_translation_is_introduced():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        language=Language.EN,
    )
    assert doc.metadata.language == Language.EN
    assert manifest.source.language == Language.EN


# T. Lineage and supersedes relationship tracking
def test_lineage_and_supersedes_relationship():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-2026-v1",
        document_id="cdc-stroke-signs-2026",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=VERIFIED_CDC_2026_TEXT,
        previous_snapshot_id="cdc-stroke-signs-2024",
        supersedes="cdc-stroke-signs-2024",
    )
    assert doc.previous_document_id == "cdc-stroke-signs-2024"
    assert doc.supersedes == "cdc-stroke-signs-2024"
    assert manifest.previous_snapshot_id == "cdc-stroke-signs-2024"
    assert manifest.supersedes == "cdc-stroke-signs-2024"
