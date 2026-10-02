import pytest
from pathlib import Path
from datetime import date, datetime, timezone
import hashlib
import json

from app.models import KnowledgeEntry, ReviewStatus, Language
from app.knowledge.loader import load_entries_dir, load_entry_file, KnowledgeLoadError
from app.knowledge.pipeline import ClinicalOnboardingPipeline, OnboardingError
from app.knowledge.retrieval import LexicalKnowledgeRetriever

def make_test_entry(
    status: ReviewStatus = ReviewStatus.DRAFT,
    version: str = "1.0",
    include_approval_meta: bool = False,
    content: str = "Synthetic validation fixture. Not medical guidance."
) -> KnowledgeEntry:
    # 1. build payload to hash
    payload = {
        "approval_metadata": {"clinical_approval_reference": "REF-123"} if include_approval_meta else {},
        "clinical_scope": "general",
        "content": content,
        "date_reviewed": "2026-01-15",
        "id": "ALPHA-001",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "Synthetic Test Source",
        "source_url": None,
        "terms": ["alpha", "synthetic"],
        "title": "Example Topic Alpha",
        "version": version
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    # 2. construct knowledge entry
    return KnowledgeEntry(
        id="ALPHA-001",
        title="Example Topic Alpha",
        terms=["alpha", "synthetic"],
        content=content,
        source="Synthetic Test Source",
        date_reviewed=date(2026, 1, 15),
        review_status=status,
        content_hash=h,
        language=Language.EN,
        version=version,
        approval_metadata={"clinical_approval_reference": "REF-123"} if include_approval_meta else {},
        reviewed_by="Dr. Synthetic" if include_approval_meta else None,
        reviewed_at=datetime(2026, 1, 15, tzinfo=timezone.utc) if include_approval_meta else None
    )

def test_pipeline_ingest_draft_and_retrieval(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    entry = make_test_entry(status=ReviewStatus.DRAFT)
    out_path = pipeline.ingest(entry)
    assert out_path.exists()
    
    # Ensure retrieval is impossible for DRAFT
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0
    retriever = LexicalKnowledgeRetriever(entries)
    from app.models import StructuredCase
    results = retriever.retrieve(StructuredCase(chief_complaint="alpha synthetic"))
    assert len(results) == 0

def test_pipeline_ingest_pending_and_rejected(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    
    entry_pend = make_test_entry(status=ReviewStatus.PENDING_DOMAIN_REVIEW, version="1.0")
    pipeline.ingest(entry_pend)
    assert len(load_entries_dir(tmp_path)) == 0
    
    entry_rej = make_test_entry(status=ReviewStatus.REJECTED, version="1.1")
    pipeline.ingest(entry_rej)
    assert len(load_entries_dir(tmp_path)) == 0

def test_pipeline_requires_approval_metadata_for_approved(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    
    # Missing approval meta
    entry_no_meta = make_test_entry(status=ReviewStatus.APPROVED, version="1.0", include_approval_meta=False)
    with pytest.raises(OnboardingError, match="requires explicit human clinical review metadata"):
        pipeline.ingest(entry_no_meta)

def test_pipeline_ingest_approved_and_retrieval(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    entry = make_test_entry(status=ReviewStatus.APPROVED, version="1.0", include_approval_meta=True)
    pipeline.ingest(entry)
    
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 1
    
    retriever = LexicalKnowledgeRetriever(entries)
    from app.models import StructuredCase
    results = retriever.retrieve(StructuredCase(chief_complaint="alpha synthetic"))
    assert len(results) == 1
    assert results[0].id == "ALPHA-001"

def test_pipeline_prevents_duplicate_versions(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    entry = make_test_entry(status=ReviewStatus.APPROVED, version="1.0", include_approval_meta=True)
    pipeline.ingest(entry)
    
    # Try to ingest same version
    with pytest.raises(OnboardingError, match="strictly greater than existing version"):
        pipeline.ingest(entry)
        
    # Try to ingest lower version
    entry_lower = make_test_entry(status=ReviewStatus.APPROVED, version="0.9", include_approval_meta=True)
    with pytest.raises(OnboardingError, match="strictly greater than existing version"):
        pipeline.ingest(entry_lower)

def test_pipeline_allows_version_upgrades(tmp_path: Path):
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    entry_v1 = make_test_entry(status=ReviewStatus.APPROVED, version="1.0", include_approval_meta=True)
    pipeline.ingest(entry_v1)
    
    entry_v2 = make_test_entry(status=ReviewStatus.APPROVED, version="2.0", include_approval_meta=True, content="Updated content")
    pipeline.ingest(entry_v2)
    
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 1
    assert entries[0].version == "2.0"
