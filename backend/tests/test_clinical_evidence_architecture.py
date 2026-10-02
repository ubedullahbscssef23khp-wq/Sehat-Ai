from __future__ import annotations
from app.knowledge.retrieval import tokenize
"""Phase 30A Clinical Knowledge & Evidence Architecture Verification Suite.

Validates:
1. Production corpus remains empty (0 EmergencyPattern, 0 KnowledgeEntry).
2. Lifecycle state enforcement (Draft, Pending, Approved, Rejected).
3. Provenance and approval metadata boundaries.
4. Deterministic content hashing and mutation invalidation.
5. Retrieval abstraction, EvidencePack assembly, and Abstention mechanics.
6. Freshness policies, language metadata, and domain routing.
7. Citation traceability and privacy preservation.
"""


from datetime import date, datetime, timezone, timedelta
import pytest

from app.models.domain import Language, ReviewStatus, StructuredCase, SymptomReport, BodySystem
from app.knowledge.evidence_models import (
    AbstentionReason,
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
    RetrievalContext,
    compute_chunk_hash,
    compute_document_hash,
)
from app.knowledge.governance import (
    GovernanceError,
    invalidate_approval_on_edit,
    promote_to_approved,
    reject_document,
    validate_for_approval,
    validate_multilingual_independence,
    validate_production_eligibility,
)
from app.knowledge.retriever import (
    ClinicalRetriever,
    LexicalClinicalRetriever,
    MockClinicalRetriever,
)
from app.knowledge.paths import CONTENT_DIR
from app.safety.paths import RULES_DIR, PRESCREEN_DIR
import glob


def make_test_document(
    terms: list[str] | None = None,
    doc_id: str = "doc-test-001",
    title: str = "Synthetic Dehydration Protocol",
    raw_content: str = "Synthetic guidance on hydration fluids and oral rehydration salts.",
    review_status: ReviewStatus = ReviewStatus.DRAFT,
    reviewed_by: str | None = None,
    reviewed_at: datetime | None = None,
    approval_ref: str | None = None,
    domain: ClinicalDomain = ClinicalDomain.GENERAL,
    language: Language = Language.EN,
    last_reviewed: date = date(2026, 1, 15),
    next_review: date | None = date(2027, 1, 15),
    version: str = "1.0",
) -> ClinicalDocument:
    source = EvidenceSource(
        name="Synthetic Public Health Organization",
        publisher="National Synthetic Health Board",
        url="https://health.synthetic.org/guidance/001",
        provenance_type="synthetic_testing_fixture",
    )
    freshness = FreshnessMetadata(
        publication_date=date(2025, 6, 1),
        last_reviewed=last_reviewed,
        next_review=next_review,
        review_interval_days=365,
    )
    metadata = EvidenceMetadata(
        domain=domain,
        category=EvidenceCategory.PUBLIC_HEALTH_ADVISORY,
        language=language,
        jurisdiction="synthetic_jurisdiction",
        clinical_scope="hydration_navigation",
        tags=["hydration", "fluids"],
    )
    content_hash = compute_document_hash(
        doc_id=doc_id,
        title=title,
        source=source,
        freshness=freshness,
        metadata=metadata,
        version=version,
        raw_content=raw_content,
    )

    approval_metadata = {}
    if approval_ref:
        approval_metadata["clinical_approval_reference"] = approval_ref

    chunk_hash = compute_chunk_hash(doc_id, 0, raw_content, language, version)
    chunk = ClinicalChunk(
        id=f"{doc_id}-c0",
        document_id=doc_id,
        chunk_index=0,
        total_chunks=1,
        content=raw_content,
        terms=terms if terms is not None else list(tokenize(title + " " + raw_content)),
        content_hash=chunk_hash,
        metadata=metadata,
    )

    return ClinicalDocument(
        id=doc_id,
        title=title,
        source=source,
        freshness=freshness,
        metadata=metadata,
        version=version,
        raw_content=raw_content,
        content_hash=content_hash,
        review_status=review_status,
        reviewed_by=reviewed_by,
        reviewed_at=reviewed_at,
        approval_metadata=approval_metadata,
        chunks=[chunk],
    )


# 1 & 2. Invariant: Production knowledge and emergency corpora are empty
def test_production_knowledge_corpus_is_empty():
    md_files = [f for f in glob.glob(str(CONTENT_DIR / "*.md")) if "readme" not in f.lower()]
    assert len(md_files) == 0, f"Production knowledge corpus must be empty, found: {md_files}"


def test_production_emergency_corpus_is_empty():
    rule_files = [f for f in glob.glob(str(RULES_DIR / "*.yaml")) if "readme" not in f.lower()]
    prescreen_files = [f for f in glob.glob(str(PRESCREEN_DIR / "*.yaml")) if "readme" not in f.lower()]
    assert len(rule_files) == 0, f"Production rules must be empty, found: {rule_files}"
    assert len(prescreen_files) == 0, f"Production prescreen must be empty, found: {prescreen_files}"


# 3, 4, 5. Lifecycle states: Draft, Pending, and Rejected cannot be retrieved as production evidence
def test_draft_content_cannot_be_retrieved():
    doc = make_test_document(review_status=ReviewStatus.DRAFT)
    retriever = LexicalClinicalRetriever([doc])
    pack = retriever.retrieve("hydration fluids")
    assert pack.should_abstain is True
    assert pack.abstention_reason == AbstentionReason.INSUFFICIENT_EVIDENCE
    assert len(pack.items) == 0


def test_pending_content_cannot_be_retrieved():
    doc = make_test_document(review_status=ReviewStatus.PENDING_DOMAIN_REVIEW)
    retriever = LexicalClinicalRetriever([doc])
    pack = retriever.retrieve("hydration fluids")
    assert pack.should_abstain is True
    assert pack.abstention_reason == AbstentionReason.INSUFFICIENT_EVIDENCE
    assert len(pack.items) == 0


def test_rejected_content_cannot_be_retrieved():
    doc = make_test_document(review_status=ReviewStatus.REJECTED)
    retriever = LexicalClinicalRetriever([doc])
    pack = retriever.retrieve("hydration fluids")
    assert pack.should_abstain is True
    assert pack.abstention_reason == AbstentionReason.INSUFFICIENT_EVIDENCE
    assert len(pack.items) == 0


# 6. Missing approval metadata blocks activation
def test_missing_approval_metadata_blocks_activation():
    doc = make_test_document(
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Dr. Synthetic Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="",  # Missing approval reference
    )
    with pytest.raises(GovernanceError, match="clinical_approval_reference"):
        validate_production_eligibility(doc)


# 7. Missing reviewer identity blocks activation
def test_missing_reviewer_blocks_activation():
    doc = make_test_document(
        review_status=ReviewStatus.APPROVED,
        reviewed_by=None,
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="REF-2026-001",
    )
    with pytest.raises(GovernanceError, match="reviewed_by"):
        validate_production_eligibility(doc)


# 8. Content hash mismatch blocks instantiation and activation
def test_invalid_content_hash_raises_validation_error():
    source = EvidenceSource(name="Synthetic", publisher="Board")
    freshness = FreshnessMetadata(last_reviewed=date(2026, 1, 1))
    metadata = EvidenceMetadata()
    with pytest.raises(ValueError, match="Document integrity failure"):
        ClinicalDocument(
            id="bad-doc",
            title="Bad Doc",
            source=source,
            freshness=freshness,
            metadata=metadata,
            raw_content="Content",
            content_hash="bad_tampered_hash_value",
            review_status=ReviewStatus.APPROVED,
        )


# 9. Modified approved content requires new review lifecycle
def test_modified_approved_content_invalidates_approval():
    doc1 = make_test_document(
        doc_id="doc-edit-1",
        version="1.0",
        raw_content="Original text",
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Dr. Synthetic",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="CLIN-REF-001",
    )
    doc2 = make_test_document(
        doc_id="doc-edit-1",
        version="1.1",
        raw_content="Mutated text",
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Dr. Synthetic",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="CLIN-REF-001",
    )

    invalidated = invalidate_approval_on_edit(doc1, doc2)
    assert invalidated.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
    assert invalidated.reviewed_by is None
    assert "clinical_approval_reference" not in invalidated.approval_metadata


# 10. Version identity remains deterministic
def test_version_identity_deterministic():
    doc_a = make_test_document(doc_id="doc-v1", version="1.0.0")
    doc_b = make_test_document(doc_id="doc-v1", version="1.0.0")
    assert doc_a.content_hash == doc_b.content_hash


# 11 & 12. Citation links to valid item and preserves provenance
def test_citation_linkage_and_provenance():
    doc = make_test_document(
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Dr. Synthetic Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="CLIN-REF-999",
    )
    retriever = LexicalClinicalRetriever([doc])
    pack = retriever.retrieve("hydration fluids")

    assert pack.should_abstain is False
    assert len(pack.items) == 1
    assert len(pack.citations) == 1

    item = pack.items[0]
    citation = pack.citations[0]
    assert citation.document_id == doc.id
    assert citation.publisher == doc.source.publisher
    assert citation.source == doc.source.name
    assert item.citation == citation
    assert "National Synthetic Health Board" in citation.provenance


# 13. Evidence sufficiency becomes INSUFFICIENT when no approved evidence exists
def test_empty_corpus_evidence_sufficiency_insufficient():
    retriever = LexicalClinicalRetriever([])
    pack = retriever.retrieve("any query")
    assert pack.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert pack.should_abstain is True
    assert pack.abstention_reason == AbstentionReason.NO_APPROVED_EVIDENCE


# 14. Freshness evaluation identifies stale content without hardcoded intervals
def test_freshness_policy_identifies_stale_content():
    policy = FreshnessPolicy(max_age_days=180, enforce_next_review=True, grace_period_days=15)
    meta = FreshnessMetadata(
        last_reviewed=date(2025, 1, 1),
        next_review=date(2025, 6, 1),
    )
    # Evaluate at a later date
    status = policy.evaluate(meta, eval_date=date(2026, 1, 1))
    assert status == FreshnessStatus.STALE

    # If within window
    fresh_meta = FreshnessMetadata(
        last_reviewed=date(2026, 1, 1),
        next_review=date(2026, 12, 31),
    )
    status_fresh = policy.evaluate(fresh_meta, eval_date=date(2026, 3, 1))
    assert status_fresh == FreshnessStatus.CURRENT


# 15. Language metadata is preserved and filtered
def test_language_filtering_in_retrieval():
    doc_en = make_test_document(doc_id="doc-en", language=Language.EN, review_status=ReviewStatus.APPROVED,
                                reviewed_by="Reviewer", reviewed_at=datetime.now(timezone.utc), approval_ref="REF-EN")
    doc_ur = make_test_document(doc_id="doc-ur", language=Language.UR, review_status=ReviewStatus.APPROVED,
                                reviewed_by="Reviewer", reviewed_at=datetime.now(timezone.utc), approval_ref="REF-UR")

    retriever = LexicalClinicalRetriever([doc_en, doc_ur])

    ctx_en = RetrievalContext(language=Language.EN)
    pack_en = retriever.retrieve("hydration fluids", context=ctx_en)
    assert len(pack_en.items) == 1
    assert pack_en.items[0].document_id == "doc-en"

    ctx_ur = RetrievalContext(language=Language.UR)
    pack_ur = retriever.retrieve("hydration fluids", context=ctx_ur)
    assert len(pack_ur.items) == 1
    assert pack_ur.items[0].document_id == "doc-ur"


# 16. Multilingual governance independence: translation cannot inherit source approval
def test_multilingual_approval_independence():
    doc_en = make_test_document(doc_id="doc-en", language=Language.EN, review_status=ReviewStatus.APPROVED,
                                approval_ref="CLIN-EN-001")
    doc_ur = make_test_document(doc_id="doc-ur", language=Language.UR, review_status=ReviewStatus.APPROVED,
                                approval_ref="CLIN-EN-001")  # Copy-pasted English approval reference

    with pytest.raises(GovernanceError, match="Multilingual governance violation"):
        validate_multilingual_independence(doc_en, doc_ur)


# 17. Domain metadata routing
def test_domain_filtering_in_retrieval():
    doc_neuro = make_test_document(
        doc_id="doc-neuro",
        domain=ClinicalDomain.NEUROLOGY,
        raw_content="Neurological protocol for headache assessment.",
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="REF-NEURO",
    )
    doc_cardio = make_test_document(
        doc_id="doc-cardio",
        domain=ClinicalDomain.CARDIOLOGY,
        raw_content="Cardiovascular protocol for chest pain triage.",
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="REF-CARDIO",
    )

    retriever = LexicalClinicalRetriever([doc_neuro, doc_cardio])

    ctx = RetrievalContext(domain=ClinicalDomain.NEUROLOGY)
    pack = retriever.retrieve("headache assessment", context=ctx)
    assert len(pack.items) == 1
    assert pack.items[0].document_id == "doc-neuro"


# 18. StructuredCase query support
def test_structured_case_retrieval_query():
    doc = make_test_document(
        raw_content="Neurological dizziness evaluation.",
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="REF-001",
    )
    retriever = LexicalClinicalRetriever([doc])

    case = StructuredCase(
        chief_complaint="persistent dizziness",
        symptoms=[SymptomReport(name="dizziness", body_system=BodySystem.NEUROLOGICAL)],
    )

    pack = retriever.retrieve(case)
    assert pack.should_abstain is False
    assert len(pack.items) == 1


def test_all_stale_evidence_triggers_abstention():
    doc = make_test_document(
        last_reviewed=date(2024, 1, 1),
        next_review=date(2024, 6, 1),
        review_status=ReviewStatus.APPROVED,
        reviewed_by="Reviewer",
        reviewed_at=datetime.now(timezone.utc),
        approval_ref="REF-STALE",
    )
    retriever = LexicalClinicalRetriever([doc])
    ctx = RetrievalContext(evaluation_date=date(2026, 1, 1))
    pack = retriever.retrieve("hydration fluids", context=ctx)
    assert pack.should_abstain is True
    assert pack.abstention_reason == AbstentionReason.STALE_EVIDENCE
    assert pack.sufficiency == EvidenceSufficiency.INSUFFICIENT


def test_mock_clinical_retriever_protocol_conformance():
    mock = MockClinicalRetriever()
    pack = mock.retrieve("test query")
    assert pack.should_abstain is True
    assert pack.sufficiency == EvidenceSufficiency.INSUFFICIENT
    assert pack.abstention_reason == AbstentionReason.INSUFFICIENT_EVIDENCE


# 20. Regression test: No universal clinical expiry assumption
def test_freshness_policy_no_universal_clinical_expiry():
    """Confirms architecture does NOT assume every clinical document expires after 365 days."""
    default_policy = FreshnessPolicy()
    assert default_policy.max_age_days is None

    # Document reviewed 3 years ago (1095 days) with no explicit next_review or policy interval
    old_valid_doc = FreshnessMetadata(
        last_reviewed=date(2023, 1, 1),
        next_review=None,
        review_interval_days=None,
    )
    # Evaluated at date(2026, 1, 1) - exactly 3 years later
    status = default_policy.evaluate(old_valid_doc, eval_date=date(2026, 1, 1))
    assert status == FreshnessStatus.CURRENT, "Must NOT expire arbitrarily after universal days"


# 21. Freshness states: CURRENT, DUE_FOR_REVIEW, STALE, UNAVAILABLE
def test_freshness_policy_explicit_states():
    policy = FreshnessPolicy(enforce_next_review=True, grace_period_days=30)

    # 1. UNAVAILABLE when review metadata is unrecorded
    unreviewed = FreshnessMetadata(last_reviewed=None, next_review=None)
    assert policy.evaluate(unreviewed, eval_date=date(2026, 3, 1)) == FreshnessStatus.UNAVAILABLE

    # 2. CURRENT when within scheduled window
    scheduled = FreshnessMetadata(
        last_reviewed=date(2026, 1, 1),
        next_review=date(2026, 6, 1),
    )
    assert policy.evaluate(scheduled, eval_date=date(2026, 3, 1)) == FreshnessStatus.CURRENT

    # 3. DUE_FOR_REVIEW when overdue but within grace period (e.g. 10 days overdue < 30 days grace)
    assert policy.evaluate(scheduled, eval_date=date(2026, 6, 11)) == FreshnessStatus.DUE_FOR_REVIEW

    # 4. STALE when overdue beyond grace period (e.g. 45 days overdue > 30 days grace)
    assert policy.evaluate(scheduled, eval_date=date(2026, 7, 16)) == FreshnessStatus.STALE


# 22. Configurable domain and jurisdiction review policies without universal expiry
def test_freshness_policy_domain_and_jurisdiction_configuration():
    policy = FreshnessPolicy(
        domain_review_intervals={ClinicalDomain.CARDIOLOGY: 180},
        jurisdiction_review_intervals={"pk": 90},
        grace_period_days=15,
    )
    # Default without explicit next_review has no universal expiry
    assert policy.max_age_days is None

    meta = FreshnessMetadata(last_reviewed=date(2026, 1, 1))

    # General domain without configured policy remains CURRENT after 200 days
    assert policy.evaluate(meta, domain=ClinicalDomain.GENERAL, eval_date=date(2026, 7, 20)) == FreshnessStatus.CURRENT

    # Cardiology domain has configured 180-day review interval:
    # At 190 days (10 days past interval, within 15-day grace) -> DUE_FOR_REVIEW
    assert policy.evaluate(meta, domain=ClinicalDomain.CARDIOLOGY, eval_date=date(2026, 7, 10)) == FreshnessStatus.DUE_FOR_REVIEW
    # At 210 days (30 days past interval, beyond 15-day grace) -> STALE
    assert policy.evaluate(meta, domain=ClinicalDomain.CARDIOLOGY, eval_date=date(2026, 7, 30)) == FreshnessStatus.STALE

    # Pakistan jurisdiction has configured 90-day review interval:
    # At 100 days (10 days past interval, within 15-day grace) -> DUE_FOR_REVIEW
    assert policy.evaluate(meta, jurisdiction="pk", eval_date=date(2026, 4, 11)) == FreshnessStatus.DUE_FOR_REVIEW


# 23. Source metadata explicit review interval
def test_freshness_policy_source_metadata_interval():
    policy = FreshnessPolicy(grace_period_days=10)
    meta = FreshnessMetadata(
        last_reviewed=date(2026, 1, 1),
        review_interval_days=90,
    )
    # At 60 days -> CURRENT
    assert policy.evaluate(meta, eval_date=date(2026, 3, 2)) == FreshnessStatus.CURRENT
    # At 95 days (5 days overdue, within 10-day grace) -> DUE_FOR_REVIEW
    assert policy.evaluate(meta, eval_date=date(2026, 4, 6)) == FreshnessStatus.DUE_FOR_REVIEW
    # At 110 days (20 days overdue, beyond 10-day grace) -> STALE
    assert policy.evaluate(meta, eval_date=date(2026, 4, 21)) == FreshnessStatus.STALE


# 24. Multilingual governance accepts qualified clinical and linguistic review
def test_multilingual_governance_qualified_linguistic_clinical_review():
    doc_en = make_test_document(
        doc_id="doc-en-valid",
        language=Language.EN,
        review_status=ReviewStatus.APPROVED,
        approval_ref="CLIN-EN-2026",
    )
    # Localized document with linguistic and clinical review metadata
    doc_ur = make_test_document(
        doc_id="doc-ur-valid",
        language=Language.UR,
        review_status=ReviewStatus.APPROVED,
        approval_ref="CLIN-EN-2026",
        reviewed_by="Qualified Bilingual Reviewer",
    )
    # Add linguistic_clinical_reviewed to approval_metadata
    updated_ur_data = doc_ur.model_dump()
    updated_ur_data["approval_metadata"]["linguistic_clinical_reviewed"] = True
    validated_ur_doc = ClinicalDocument.model_validate(updated_ur_data)

    # Should succeed without GovernanceError
    validate_multilingual_independence(doc_en, validated_ur_doc)

