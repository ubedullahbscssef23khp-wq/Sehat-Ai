import pytest
from pathlib import Path
from datetime import date, datetime, timezone
import hashlib
import json
from fastapi.testclient import TestClient

from app.models import KnowledgeEntry, ReviewStatus, Language, EmergencyPattern
from app.knowledge.loader import load_entries_dir, KnowledgeLoadError
from app.knowledge.pipeline import ClinicalOnboardingPipeline, OnboardingError
from app.knowledge.retrieval import LexicalKnowledgeRetriever
from app.safety.loader import load_patterns_dir
from app.main import create_app
from app.core.config import Settings
from app.persistence.database import build_engine

# --- Tests for Mechanical Onboarding of Clinical Vertical Slice (Stroke/BEFAST) ---

def make_test_befast_entry(
    tmp_path: Path, 
    status: ReviewStatus = ReviewStatus.APPROVED, 
    lang: Language = Language.EN,
    version: str = "1.0",
    mutate_hash: bool = False
) -> Path:
    pipeline = ClinicalOnboardingPipeline(tmp_path)
    
    # We must explicitly add approval_metadata for approved entries
    approval_meta = {"clinical_approval_reference": "TEST-REF-999"} if status == ReviewStatus.APPROVED else {}
    
    payload = {
        "approval_metadata": approval_meta,
        "clinical_scope": "stroke",
        "content": "Synthetic BEFAST stroke guidance. Sudden facial droop requires emergency attention.",
        "date_reviewed": "2026-02-15",
        "id": f"BEFAST-F-001-{lang.value.upper()}",
        "language": lang.value,
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "Synthetic Mock Source",
        "source_url": None,
        "terms": ["facial droop", "stroke", "face"],
        "title": "BEFAST Facial Droop",
        "version": version
    }
    
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    if mutate_hash:
        h = "0" * 64

    entry = KnowledgeEntry(
        id=payload["id"],
        title=payload["title"],
        terms=payload["terms"],
        content=payload["content"],
        source=payload["source"],
        date_reviewed=date(2026, 2, 15),
        review_status=status,
        content_hash=h,
        language=lang,
        version=version,
        approval_metadata=approval_meta,
        reviewed_by="Dr. Synthetic Test" if approval_meta else None,
        reviewed_at=datetime(2026, 2, 15, tzinfo=timezone.utc) if approval_meta else None,
        clinical_scope="stroke"
    )
    
    return pipeline.ingest(entry)

def write_mock_emergency_patterns(tmp_path: Path, patterns: list[dict]):
    import yaml
    (tmp_path / "befast.yaml").write_text(yaml.dump({"patterns": patterns}))

def test_befast_approved_pattern_activates(tmp_path: Path):
    write_mock_emergency_patterns(tmp_path, [{
        "id": "BEFAST-F-001",
        "pattern": "facial droop",
        "description": "Sudden facial weakness or drooping",
        "source": "Synthetic Source",
        "review_date": "2026-02-15",
        "review_status": "approved"
    }])
    patterns = load_patterns_dir(tmp_path)
    assert len(patterns) == 1
    assert patterns[0].id == "BEFAST-F-001"

def test_befast_unapproved_pattern_does_not_activate(tmp_path: Path):
    write_mock_emergency_patterns(tmp_path, [{
        "id": "BEFAST-F-001",
        "pattern": "facial droop",
        "description": "Sudden facial weakness or drooping",
        "source": "Synthetic Source",
        "review_date": "2026-02-15",
        "review_status": "pending_domain_review"
    }])
    patterns = load_patterns_dir(tmp_path)
    assert len(patterns) == 0

def test_befast_modified_approved_content_requires_re_review(tmp_path: Path):
    out_path = make_test_befast_entry(tmp_path, status=ReviewStatus.APPROVED, version="1.0")
    
    # modify content directly (tampering)
    text = out_path.read_text(encoding="utf-8")
    tampered_text = text.replace("Sudden facial droop", "Gradual facial droop")
    out_path.write_text(tampered_text, encoding="utf-8")
    
    from app.knowledge.loader import load_entry_file
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entry_file(out_path)

def test_befast_evidence_preserves_metadata(tmp_path: Path):
    make_test_befast_entry(tmp_path, status=ReviewStatus.APPROVED, version="1.0")
    entries = load_entries_dir(tmp_path)
    retriever = LexicalKnowledgeRetriever(entries)
    
    from app.models import StructuredCase
    case = StructuredCase(chief_complaint="I have a sudden facial droop")
    results = retriever.retrieve(case)
    
    assert len(results) == 1
    assert results[0].id == "BEFAST-F-001-EN"
    assert results[0].source == "Synthetic Mock Source"
    assert results[0].version == "1.0"
    assert results[0].review_status == ReviewStatus.APPROVED
    assert results[0].language == Language.EN

def test_befast_multilingual_independence(tmp_path: Path):
    # Approving English does not approve Urdu
    make_test_befast_entry(tmp_path, status=ReviewStatus.APPROVED, lang=Language.EN, version="1.0")
    make_test_befast_entry(tmp_path, status=ReviewStatus.PENDING_DOMAIN_REVIEW, lang=Language.UR, version="1.0")
    
    entries = load_entries_dir(tmp_path)
    
    # Only EN should be loaded
    assert len(entries) == 1
    assert entries[0].language == Language.EN
    assert entries[0].id == "BEFAST-F-001-EN"

def test_befast_unicode_nfc_intact(tmp_path: Path):
    import unicodedata
    # é (e + combining acute accent) vs é (precomposed)
    nfd_pattern = "fac\u0069\u0301al droop" # facíal droop
    nfc_pattern = unicodedata.normalize("NFC", nfd_pattern)
    
    write_mock_emergency_patterns(tmp_path, [{
        "id": "BEFAST-F-001",
        "pattern": nfc_pattern,
        "description": "Sudden facial weakness or drooping",
        "source": "Synthetic Source",
        "review_date": "2026-02-15",
        "review_status": "approved"
    }])
    patterns = load_patterns_dir(tmp_path)
    
    from app.safety.prescreen import evaluate_prescreen
    # matching should be deterministic and casefolded/nfc
    fires = evaluate_prescreen(patterns, "I have " + nfd_pattern.upper())
    assert len(fires) == 1
    assert fires[0].id == "BEFAST-F-001"
    
def test_befast_llm_cannot_override_deterministic_escalation(tmp_path: Path):
    # Set up app with synthetic emergency pattern
    write_mock_emergency_patterns(tmp_path, [{
        "id": "BEFAST-F-001",
        "pattern": "facial droop",
        "description": "Sudden facial weakness or drooping",
        "source": "Synthetic Source",
        "review_date": "2026-02-15",
        "review_status": "approved"
    }])
    
    settings = Settings(
        sehat_env="development",
        sehat_llm_provider="mock",
        sehat_db_path=tmp_path / "api.sqlite",
        _env_file=None,
    )
    
    app = create_app(settings=settings)
    
    from app.llm.mock import MockProvider
    from app.conversation.orchestrator import ConversationOrchestrator
    from tests.conversation_support import case_json
    from sqlalchemy.orm import sessionmaker
    
    # Mock LLM gives a "no emergency" output
    provider = MockProvider([case_json(chief_complaint="Facial droop but I think I am fine")])
    engine = build_engine(settings.sehat_db_path)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    
    patterns = load_patterns_dir(tmp_path)
    
    app.state.orchestrator = ConversationOrchestrator(
        provider=provider,
        session_factory=session_factory,
        rules=[],
        prescreen_patterns=patterns,
        max_followup_rounds=settings.sehat_max_followup_rounds,
        knowledge=[],
    )
    
    with TestClient(app) as client:
        res = client.post("/sessions", json={})
        session_id = res.json()["id"]
        
        # User explicitly triggers emergency prescreen
        res = client.post(f"/sessions/{session_id}/messages", json={"text": "I have sudden facial droop"})
        assert res.status_code == 200
        
        data = res.json()
        assert data["triage"]["level"] == "emergency" # Overrides the mock LLM because prescreen fires
        assert "BEFAST-F-001" in data["triage"]["fired_rule_ids"]
        assert len(data["disclaimers"]) > 0
        
def test_befast_empty_knowledge_state_remains_safe(tmp_path: Path):
    # No knowledge, no patterns
    settings = Settings(
        sehat_env="development",
        sehat_llm_provider="mock",
        sehat_db_path=tmp_path / "api.sqlite",
        _env_file=None,
    )
    
    app = create_app(settings=settings)
    
    from app.llm.mock import MockProvider
    from app.conversation.orchestrator import ConversationOrchestrator
    from tests.conversation_support import case_json
    from sqlalchemy.orm import sessionmaker
    
    provider = MockProvider([case_json(chief_complaint="General health inquiry")])
    engine = build_engine(settings.sehat_db_path)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    
    app.state.orchestrator = ConversationOrchestrator(
        provider=provider,
        session_factory=session_factory,
        rules=[],
        prescreen_patterns=[],
        max_followup_rounds=settings.sehat_max_followup_rounds,
        knowledge=[],
    )
    
    with TestClient(app) as client:
        res = client.post("/sessions", json={})
        session_id = res.json()["id"]
        
        res = client.post(f"/sessions/{session_id}/messages", json={"text": "Hello"})
        assert res.status_code == 200
        
        data = res.json()
        assert "triage" in data
        assert len(data.get("evidence", [])) == 0 # no crashes despite empty

