import pytest
from pathlib import Path
from datetime import date
import hashlib
import json

from fastapi.testclient import TestClient

from app.models import ReviewStatus
from app.knowledge.loader import load_entry_file, load_entries_dir, KnowledgeLoadError
from app.knowledge.paths import CONTENT_DIR
from app.knowledge.retrieval import LexicalKnowledgeRetriever
from app.main import create_app
from app.core.config import Settings
from app.persistence.database import build_engine

def make_test_entry(tmp_path: Path, status: str = "approved", mutate_hash: bool = False, mutate_body: bool = False) -> str:
    body = "Disorders of the nervous system."
    if mutate_body:
        body = "Disorders."
        
    payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": body,
        "date_reviewed": "2026-01-15",
        "id": "HEADACHE-001",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "WHO",
        "source_url": None,
        "terms": ["headache", "head pain"],
        "title": "General headache information",
        "version": "1.0"
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    if mutate_hash:
        h = "0" * 64
        
    text = f"""---
id: HEADACHE-001
title: General headache information
terms: [headache, head pain]
source: WHO
date_reviewed: 2026-01-15
review_status: {status}
content_hash: '{h}'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
{body}"""
    test_file = tmp_path / "HEADACHE-001.md"
    test_file.write_text(text, encoding="utf-8")
    return text

def test_production_loader_excludes_pending_entries(tmp_path: Path) -> None:
    make_test_entry(tmp_path, "pending_domain_review")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0

def test_production_retrieval_returns_zero_headache_entries(tmp_path: Path) -> None:
    make_test_entry(tmp_path, "pending_domain_review")
    retriever = LexicalKnowledgeRetriever(load_entries_dir(tmp_path))
    from app.models import StructuredCase
    case = StructuredCase(chief_complaint="migraine headache tension")
    results = retriever.retrieve(case)
    assert len(results) == 0

def test_synthetic_approved_copy_can_be_retrieved(tmp_path: Path) -> None:
    make_test_entry(tmp_path, "approved")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 1
    assert entries[0].review_status == ReviewStatus.APPROVED
    
    retriever = LexicalKnowledgeRetriever(entries)
    from app.models import StructuredCase
    case = StructuredCase(chief_complaint="headache disorder nervous system")
    results = retriever.retrieve(case)
    assert len(results) == 1
    assert results[0].id == "HEADACHE-001"
    assert results[0].source == "WHO"
    assert results[0].date_reviewed == date(2026, 1, 15)

def test_modifying_real_content_invalidates_hash(tmp_path: Path) -> None:
    make_test_entry(tmp_path, mutate_hash=True)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entry_file(tmp_path / "HEADACHE-001.md")
        
    make_test_entry(tmp_path, mutate_body=True) # Hashes properly calculated for bad body? 
    # Wait, make_test_entry automatically hashes the body. We need to manually write a bad file.
    
    # Hand-craft a mismatched file:
    text = make_test_entry(tmp_path)
    bad_content = text.replace("Disorders of the nervous system.", "Disorders.")
    (tmp_path / "mod_content.md").write_text(bad_content, encoding="utf-8")
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entry_file(tmp_path / "mod_content.md")

def test_realistic_end_to_end_headache_scenario(tmp_path: Path) -> None:
    make_test_entry(tmp_path, "approved")
    
    settings = Settings(
        sehat_env="development",
        sehat_llm_provider="mock",
        sehat_db_path=tmp_path / "api.sqlite",
        _env_file=None,
    )
    
    app = create_app(settings=settings)
    
    approved_entries = load_entries_dir(tmp_path)
    test_retriever = LexicalKnowledgeRetriever(approved_entries)
    
    from app.llm.mock import MockProvider
    from app.conversation.orchestrator import ConversationOrchestrator
    from tests.conversation_support import case_json
    from sqlalchemy.orm import sessionmaker
    
    provider = MockProvider([case_json(chief_complaint="I have a terrible headache disorder")])
    engine = build_engine(settings.sehat_db_path)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, future=True)
    
    app.state.orchestrator = ConversationOrchestrator(
        provider=provider,
        session_factory=session_factory,
        rules=[],
        prescreen_patterns=[],
        max_followup_rounds=settings.sehat_max_followup_rounds,
        knowledge=approved_entries,
    )
    
    with TestClient(app) as client:
        res = client.post("/sessions", json={})
        assert res.status_code == 201
        session_id = res.json()["id"]
        
        res = client.post(f"/sessions/{session_id}/messages", json={"text": "headache"})
        assert res.status_code == 200
        
        data = res.json()
        assert data["triage"] is not None
        
        evidence = data.get("evidence", [])
        assert len(evidence) > 0
        assert "source" in evidence[0]
        assert "WHO" in evidence[0]["source"]
        assert "date_reviewed" in evidence[0]
