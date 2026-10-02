"""Phase 30B: First Authoritative Clinical Evidence Ingestion Verification.

Tests the full lifecycle of authoritative evidence ingestion, deterministic chunking,
provenance preservation, governance gating, and abstention behavior.

GOVERNANCE INVARIANTS:
1. Newly ingested content has review_status == PENDING_DOMAIN_REVIEW.
2. Unreviewed, draft, pending, or rejected content CANNOT enter production retrieval.
3. Production corpus count remains 0 until clinical review panel sign-off.
4. No fake reviewer, approval reference, or medical claims are created.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
import hashlib
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
    invalidate_approval_on_edit,
    promote_to_approved,
    reject_document,
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

SAMPLE_CDC_TEXT = (
    "Signs and symptoms of stroke: During a stroke, every minute counts! "
    "Fast treatment can lessen the brain damage that stroke can cause.\n\n"
    "Signs of stroke in men and women include: Sudden numbness or weakness in the face, "
    "arm, or leg, especially on one side of the body.\n\n"
    "Sudden confusion, trouble speaking, or difficulty understanding speech.\n\n"
    "Sudden trouble seeing in one or both eyes.\n\n"
    "Sudden trouble walking, dizziness, loss of balance, or lack of coordination.\n\n"
    "Sudden severe headache with no known cause.\n\n"
    "Call 9-1-1 right away if you or someone else has any of these symptoms. Act F.A.S.T.: "
    "Face drooping, Arm weakness, Speech difficulty, Time to call 9-1-1."
)


# 1. Source manifest validation
def test_source_manifest_validation():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
        publication_date=date(2024, 5, 1),
        source_version="1.0",
        language=Language.EN,
        clinical_domain=ClinicalDomain.NEUROLOGY,
        jurisdiction="US / Global Public Health",
    )
    assert manifest.source_id == "src-cdc-stroke-signs-v1"
    assert manifest.publisher == "Centers for Disease Control and Prevention"
    assert manifest.title == "Signs and Symptoms of Stroke"
    assert manifest.canonical_url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert manifest.publication_date == date(2024, 5, 1)
    assert manifest.language == Language.EN
    assert manifest.clinical_domain == ClinicalDomain.NEUROLOGY
    assert manifest.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
    assert manifest.chunks_count == 7
    assert manifest.content_hash == doc.content_hash
    assert len(manifest.raw_content_sha256) == 64


# 2. Canonical URL and provenance validation
def test_canonical_url_and_provenance_validation():
    # Valid https URL
    validate_source_provenance("CDC", "Stroke Signs", "https://www.cdc.gov/stroke")
    # Valid http URL
    validate_source_provenance("CDC", "Stroke Signs", "http://example.org/stroke")

    # Invalid URL scheme
    with pytest.raises(IngestionError, match="Invalid canonical_url format"):
        validate_source_provenance("CDC", "Stroke Signs", "ftp://example.org")

    with pytest.raises(IngestionError, match="Invalid canonical_url format"):
        validate_source_provenance("CDC", "Stroke Signs", "not-a-url")


# 3. Source hash generation and reproducibility
def test_source_hash_generation_is_reproducible():
    doc1, manifest1 = ingest_authoritative_source(
        source_id="src-test-01",
        document_id="doc-test-01",
        publisher="Authoritative Health Org",
        title="Clinical Topic A",
        canonical_url="https://example.org/topic-a",
        raw_content=SAMPLE_CDC_TEXT,
        publication_date=date(2025, 1, 1),
    )
    doc2, manifest2 = ingest_authoritative_source(
        source_id="src-test-01",
        document_id="doc-test-01",
        publisher="Authoritative Health Org",
        title="Clinical Topic A",
        canonical_url="https://example.org/topic-a",
        raw_content=SAMPLE_CDC_TEXT,
        publication_date=date(2025, 1, 1),
    )
    assert doc1.content_hash == doc2.content_hash
    assert manifest1.raw_content_sha256 == manifest2.raw_content_sha256
    assert [c.content_hash for c in doc1.chunks] == [c.content_hash for c in doc2.chunks]


# 4. Deterministic document identity
def test_deterministic_document_identity():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    assert doc.id == "cdc-stroke-signs-2024"
    assert doc.version == "1.0"
    assert doc.title == "Signs and Symptoms of Stroke"


# 5. Deterministic chunk identity
def test_deterministic_chunk_identity():
    meta = EvidenceMetadata(domain=ClinicalDomain.NEUROLOGY, language=Language.EN)
    chunks = extract_clinical_chunks(
        document_id="doc-stroke-1",
        raw_content=SAMPLE_CDC_TEXT,
        language=Language.EN,
        version="1.0",
        metadata=meta,
    )
    assert len(chunks) == 7
    expected_ids = [f"doc-stroke-1-chk-{i:02d}" for i in range(7)]
    assert [c.id for c in chunks] == expected_ids
    assert [c.chunk_index for c in chunks] == list(range(7))
    assert all(c.total_chunks == 7 for c in chunks)


# 6. Chunk provenance inheritance
def test_chunk_provenance_inheritance():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
        clinical_domain=ClinicalDomain.NEUROLOGY,
        language=Language.EN,
    )
    for chunk in doc.chunks:
        assert chunk.document_id == doc.id
        assert chunk.metadata.domain == ClinicalDomain.NEUROLOGY
        assert chunk.metadata.language == Language.EN
        assert chunk.start_char is not None
        assert chunk.end_char is not None
        assert chunk.end_char > chunk.start_char
        # Excerpt matches raw content slice
        assert doc.raw_content[chunk.start_char:chunk.end_char] == chunk.content


# 7. Missing provenance rejection
def test_missing_provenance_rejection():
    with pytest.raises(IngestionError, match="publisher must not be empty"):
        ingest_authoritative_source(
            source_id="s1",
            document_id="d1",
            publisher="",
            title="Stroke",
            canonical_url="https://example.org",
            raw_content="Text",
        )

    with pytest.raises(IngestionError, match="canonical_url must not be empty"):
        ingest_authoritative_source(
            source_id="s1",
            document_id="d1",
            publisher="CDC",
            title="Stroke",
            canonical_url="",
            raw_content="Text",
        )


# 8. Missing source identity rejection
def test_missing_source_identity_rejection():
    with pytest.raises(IngestionError, match="title must not be empty"):
        ingest_authoritative_source(
            source_id="s1",
            document_id="d1",
            publisher="CDC",
            title="",
            canonical_url="https://example.org",
            raw_content="Text",
        )

    with pytest.raises(IngestionError, match="raw_content must not be empty"):
        ingest_authoritative_source(
            source_id="s1",
            document_id="d1",
            publisher="CDC",
            title="Stroke",
            canonical_url="https://example.org",
            raw_content="   ",
        )


# 9. Pending content cannot enter production retrieval
def test_pending_content_cannot_enter_production_retrieval():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    assert doc.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW

    retriever = LexicalClinicalRetriever([doc])
    ctx = RetrievalContext(allow_unreviewed=False)
    pack = retriever.retrieve("facial droop weakness numbness", context=ctx)

    assert pack.should_abstain is True
    assert pack.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert pack.abstention_reason in (AbstentionReason.NO_APPROVED_EVIDENCE, AbstentionReason.INSUFFICIENT_EVIDENCE)
    assert len(pack.items) == 0


# 10. Rejected content cannot enter production retrieval
def test_rejected_content_cannot_enter_production_retrieval():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    rejected_doc = reject_document(
        doc,
        reviewer_name="Dr. Clinical Reviewer",
        reason="Does not meet local deployment scope",
    )
    assert rejected_doc.review_status == ReviewStatus.REJECTED

    retriever = LexicalClinicalRetriever([rejected_doc])
    pack = retriever.retrieve("stroke weakness", context=RetrievalContext(allow_unreviewed=False))

    assert pack.should_abstain is True
    assert pack.abstention_reason in (AbstentionReason.NO_APPROVED_EVIDENCE, AbstentionReason.INSUFFICIENT_EVIDENCE)
    assert len(pack.items) == 0


# 11. Draft content cannot enter production retrieval
def test_draft_content_cannot_enter_production_retrieval():
    doc_data = {
        "id": "draft-stroke-01",
        "title": "Draft Stroke Document",
        "source": {"name": "Draft Source", "publisher": "Draft Publisher"},
        "freshness": {"last_reviewed": None},
        "metadata": {"domain": "neurology", "language": "en"},
        "version": "1.0",
        "raw_content": "Draft unverified clinical text.",
        "content_hash": "dummy_hash",
        "review_status": "draft",
    }
    # Calculate valid hash
    h = compute_document_hash(
        doc_id="draft-stroke-01",
        title="Draft Stroke Document",
        source=EvidenceSource(name="Draft Source", publisher="Draft Publisher"),
        freshness=FreshnessMetadata(last_reviewed=None),
        metadata=EvidenceMetadata(domain=ClinicalDomain.NEUROLOGY, language=Language.EN),
        version="1.0",
        raw_content="Draft unverified clinical text.",
    )
    doc_data["content_hash"] = h
    draft_doc = ClinicalDocument.model_validate(doc_data)

    retriever = LexicalClinicalRetriever([draft_doc])
    pack = retriever.retrieve("draft text", context=RetrievalContext(allow_unreviewed=False))

    assert pack.should_abstain is True
    assert pack.abstention_reason in (AbstentionReason.NO_APPROVED_EVIDENCE, AbstentionReason.INSUFFICIENT_EVIDENCE)
    assert len(pack.items) == 0


# 12. Approved content requires valid approval metadata
def test_approved_content_requires_valid_approval_metadata():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    # Attempting to validate for approval while in PENDING_DOMAIN_REVIEW
    with pytest.raises(GovernanceError, match="requires non-empty human reviewer identity"):
        validate_for_approval(doc)

    # Empty approval reference raises GovernanceError
    with pytest.raises(GovernanceError, match="Clinical approval reference cannot be empty"):
        promote_to_approved(doc, reviewer_name="Dr. Qualified", approval_ref="")

    # Empty reviewer raises GovernanceError
    with pytest.raises(GovernanceError, match="Reviewer name cannot be empty"):
        promote_to_approved(doc, reviewer_name="", approval_ref="REF-01")


# 13. Content mutation invalidates approval
def test_content_mutation_invalidates_approval():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    # Synthetically promote in isolated unit test
    approved_doc = promote_to_approved(
        doc,
        reviewer_name="Dr. Neurologist MD",
        approval_ref="CLIN-CDC-STROKE-2026",
        notes="Verified verbatim from CDC",
    )
    assert approved_doc.review_status == ReviewStatus.APPROVED

    # Simulate mutated content with updated hash
    new_content = approved_doc.raw_content + " Mutated non-CDC text."
    new_hash = compute_document_hash(
        doc_id=approved_doc.id,
        title=approved_doc.title,
        source=approved_doc.source,
        freshness=approved_doc.freshness,
        metadata=approved_doc.metadata,
        version=approved_doc.version,
        raw_content=new_content,
    )
    mutated_doc = approved_doc.model_copy(
        update={
            "raw_content": new_content,
            "content_hash": new_hash,
        }
    )
    invalidated = invalidate_approval_on_edit(approved_doc, mutated_doc)
    assert invalidated.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
    assert invalidated.reviewed_by is None
    assert "clinical_approval_reference" not in invalidated.approval_metadata


# 14. Citation points to the correct document and chunk
def test_citation_points_to_correct_document_and_chunk():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    # Promote inside isolated test fixture only
    approved_doc = promote_to_approved(
        doc,
        reviewer_name="Dr. Neurologist MD",
        approval_ref="CLIN-TEST-2026",
    )

    retriever = LexicalClinicalRetriever([approved_doc])
    pack = retriever.retrieve("facial numbness weakness drooping", context=RetrievalContext(allow_unreviewed=False))

    assert pack.should_abstain is False
    assert len(pack.items) >= 1
    top_item = pack.items[0]
    assert top_item.document_id == "cdc-stroke-signs-2024"
    assert top_item.chunk.id.startswith("cdc-stroke-signs-2024-chk-")
    assert top_item.citation.source == "Signs and Symptoms of Stroke"
    assert top_item.citation.publisher == "Centers for Disease Control and Prevention"
    assert top_item.citation.url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert top_item.citation.chunk_id == top_item.chunk.id


# 15. EvidencePack preserves source provenance
def test_evidence_pack_preserves_source_provenance():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    approved_doc = promote_to_approved(
        doc,
        reviewer_name="Dr. Neurologist MD",
        approval_ref="CLIN-TEST-2026",
    )
    retriever = LexicalClinicalRetriever([approved_doc])
    pack = retriever.retrieve("slurred speech trouble speaking", context=RetrievalContext(allow_unreviewed=False))

    assert len(pack.citations) >= 1
    citation = pack.citations[0]
    assert citation.publisher == "Centers for Disease Control and Prevention"
    assert citation.url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert "Centers for Disease Control and Prevention" in citation.provenance


# 16. Empty/insufficient evidence triggers abstention
def test_empty_or_unmatched_query_triggers_abstention():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    approved_doc = promote_to_approved(doc, reviewer_name="Dr. MD", approval_ref="REF")
    retriever = LexicalClinicalRetriever([approved_doc])

    # Unmatched query (completely different domain)
    pack = retriever.retrieve("fractured femur bone repair orthopedic surgery")
    assert pack.should_abstain is True
    assert pack.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert pack.abstention_reason == AbstentionReason.INSUFFICIENT_EVIDENCE


# 17. Language metadata is preserved and filtered
def test_language_metadata_is_preserved_and_filtered():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
        language=Language.EN,
    )
    approved_doc = promote_to_approved(doc, reviewer_name="Dr. MD", approval_ref="REF")
    retriever = LexicalClinicalRetriever([approved_doc])

    # English query context matches
    pack_en = retriever.retrieve("sudden severe headache", context=RetrievalContext(language=Language.EN))
    assert pack_en.should_abstain is False
    assert len(pack_en.items) >= 1

    # Urdu query context filters out English document without translation approval
    pack_ur = retriever.retrieve("sudden severe headache", context=RetrievalContext(language=Language.UR))
    assert pack_ur.should_abstain is True
    assert pack_ur.abstention_reason in (AbstentionReason.NO_APPROVED_EVIDENCE, AbstentionReason.INSUFFICIENT_EVIDENCE)


# 18. Clinical domain metadata is preserved and filtered
def test_clinical_domain_metadata_is_preserved_and_filtered():
    doc, _ = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
        clinical_domain=ClinicalDomain.NEUROLOGY,
    )
    approved_doc = promote_to_approved(doc, reviewer_name="Dr. MD", approval_ref="REF")
    retriever = LexicalClinicalRetriever([approved_doc])

    # Matching domain (NEUROLOGY)
    pack_neuro = retriever.retrieve("balance dizziness", context=RetrievalContext(domain=ClinicalDomain.NEUROLOGY))
    assert pack_neuro.should_abstain is False

    # Mismatched domain (CARDIOLOGY)
    pack_cardio = retriever.retrieve("balance dizziness", context=RetrievalContext(domain=ClinicalDomain.CARDIOLOGY))
    assert pack_cardio.should_abstain is True


# 19. Production corpus contains only explicitly eligible content
def test_production_corpus_has_zero_unreviewed_entries():
    entries = load_entries_dir(CONTENT_DIR)
    assert len(entries) == 0, "Production knowledge corpus must be 0 entries until clinical activation."


# 20. No fabricated clinical content exists in production
def test_no_fabricated_clinical_content_in_production():
    entries = load_entries_dir(CONTENT_DIR)
    for entry in entries:
        assert entry.review_status == ReviewStatus.APPROVED
        assert entry.reviewed_by is not None
        assert entry.approval_metadata.get("clinical_approval_reference") is not None


# 21. Source metadata strictly separated from ingestion metadata (Phase 30B-H)
def test_source_metadata_strictly_separated_from_ingestion_metadata():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
        official_source_version=None,
        internal_version="1.0",
        verification_status="authoritative_retrieval_verified_differences_reported",
    )
    # Check typed segregation
    assert isinstance(manifest.source, AuthoritativeSourceMetadata)
    assert isinstance(manifest.ingestion, IngestionMetadata)

    # Authoritative source facts
    assert manifest.source.publisher == "Centers for Disease Control and Prevention"
    assert manifest.source.title == "Signs and Symptoms of Stroke"
    assert manifest.source.canonical_url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert manifest.source.official_publication_date == date(2024, 5, 15)
    assert manifest.source.official_update_date == date(2026, 5, 19)
    assert manifest.source.official_version is None

    # Pipeline ingestion artifacts
    assert manifest.ingestion.ingestion_id == "src-cdc-stroke-signs-v1"
    assert manifest.ingestion.internal_version == "1.0"
    assert manifest.ingestion.ingestion_method == IngestionMethod.CURATED_SNAPSHOT
    assert manifest.ingestion.verification_status == "authoritative_retrieval_verified_differences_reported"
    assert manifest.ingestion.raw_content_sha256 == doc.content_hash or len(manifest.ingestion.raw_content_sha256) == 64


# 22. Official version vs internal version distinction
def test_official_version_vs_internal_version_distinction():
    _, manifest = ingest_authoritative_source(
        source_id="src-test-v1",
        document_id="doc-test-1",
        publisher="CDC",
        title="Test Stroke Signs",
        canonical_url="https://www.cdc.gov/test",
        raw_content="Test stroke content paragraph.",
        official_source_version=None,  # CDC web pages do not issue official clinical versions
        internal_version="1.0",        # SehatAI internal pipeline ingestion version
    )
    assert manifest.source.official_version is None
    assert manifest.source_version is None
    assert manifest.ingestion.internal_version == "1.0"
    assert manifest.internal_version == "1.0"


# 23. Official publication and update dates recorded without synthetic invention
def test_official_publication_and_update_dates_handling():
    # Case A: Explicit official publication and update dates provided
    _, manifest_with_dates = ingest_authoritative_source(
        source_id="src-cdc-dates",
        document_id="doc-cdc-dates",
        publisher="CDC",
        title="Signs and Symptoms",
        canonical_url="https://www.cdc.gov/signs",
        raw_content="Signs content paragraph.",
        official_publication_date=date(2024, 5, 15),
        official_update_date=date(2026, 5, 19),
    )
    assert manifest_with_dates.source.official_publication_date == date(2024, 5, 15)
    assert manifest_with_dates.source.official_update_date == date(2026, 5, 19)

    # Case B: When publication date is unavailable from source, it remains None rather than fabricated
    _, manifest_without_dates = ingest_authoritative_source(
        source_id="src-nodate",
        document_id="doc-nodate",
        publisher="Public Health Entity",
        title="General Warning Signs",
        canonical_url="https://example.org/guideline",
        raw_content="General advisory paragraph.",
        official_publication_date=None,
        official_update_date=None,
    )
    assert manifest_without_dates.source.official_publication_date is None
    assert manifest_without_dates.source.official_update_date is None


# 24. Elimination of overclaiming language in generated review package
def test_removal_of_overclaiming_language_in_review_package():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-audit",
        document_id="cdc-stroke-audit",
        publisher="CDC",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    md = generate_review_package_markdown(doc, manifest)

    # Required precise integrity phrasing
    assert (
        "Stored excerpts are preserved from the ingested source snapshot; "
        "provenance and integrity are cryptographically tracked." in md
    )

    # Forbidden overclaiming phrases
    lower_md = md.lower()
    assert "zero hallucination" not in lower_md
    assert "zero medical hallucination" not in lower_md
    assert "guaranteed accurate" not in lower_md
    assert "100% correct" not in lower_md


# 25. Staged CDC manifest file on disk conforms strictly to SourceManifest schema
def test_staged_cdc_manifest_file_structure_and_integrity():
    import json
    manifest_path = Path(__file__).resolve().parent.parent / "app" / "knowledge" / "manifests" / "cdc_stroke_signs_manifest.json"
    assert manifest_path.exists(), f"Expected manifest file at {manifest_path}"

    with open(manifest_path, encoding="utf-8") as f:
        data = json.load(f)

    # Strict structure checks
    assert "source" in data, "Manifest must have top-level 'source' object."
    assert "ingestion" in data, "Manifest must have top-level 'ingestion' object."

    manifest = SourceManifest.model_validate(data)
    assert manifest.source.publisher == "Centers for Disease Control and Prevention"
    assert manifest.source.title == "Signs and Symptoms of Stroke"
    assert manifest.source.canonical_url == "https://www.cdc.gov/stroke/signs-symptoms/index.html"
    assert manifest.source.official_publication_date == date(2024, 5, 15)
    assert manifest.source.official_update_date == date(2026, 5, 19)
    assert manifest.source.official_version is None
    assert manifest.ingestion.internal_version == "1.0"
    assert manifest.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW


# 26. Staged CDC document remains pending with zero fake reviewer or approval
def test_staged_cdc_document_remains_pending_with_zero_fake_reviewer():
    doc, manifest = ingest_authoritative_source(
        source_id="src-cdc-stroke-signs-v1",
        document_id="cdc-stroke-signs-2024",
        publisher="Centers for Disease Control and Prevention",
        title="Signs and Symptoms of Stroke",
        canonical_url="https://www.cdc.gov/stroke/signs-symptoms/index.html",
        raw_content=SAMPLE_CDC_TEXT,
    )
    assert doc.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
    assert doc.reviewed_by is None
    assert doc.reviewed_at is None
    assert doc.approval_metadata == {}
    assert manifest.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW


# 27. Production corpus remains strictly zero entries
def test_production_corpus_and_emergency_patterns_remain_zero():
    entries = load_entries_dir(CONTENT_DIR)
    assert len(entries) == 0, "Production knowledge entries MUST remain 0."

