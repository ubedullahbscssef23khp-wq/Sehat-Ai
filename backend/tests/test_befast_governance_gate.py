import pytest
from pathlib import Path
from app.knowledge.loader import load_entries_dir, load_entry_file, parse_entry, KnowledgeLoadError
from app.safety.loader import load_patterns_dir, parse_patterns, RuleLoadError
from app.knowledge.paths import CONTENT_DIR
from app.safety.paths import PRESCREEN_DIR
from app.models import ReviewStatus, KnowledgeEntry

def test_production_emergency_corpus_is_empty():
    patterns = load_patterns_dir(PRESCREEN_DIR)
    assert len(patterns) == 0, "Production emergency corpus MUST be empty until clinical review."

def test_production_knowledge_corpus_is_empty():
    entries = load_entries_dir(CONTENT_DIR)
    assert len(entries) == 0, "Production knowledge corpus MUST be empty until clinical review."

def test_pending_knowledge_cannot_activate(tmp_path):
    pending_content = """---
id: test-pending
title: Test Pending
source: CDC
source_url: https://example.com
publication_date: 2026-05-01
date_reviewed: 2026-09-12
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
language: en
clinical_scope: stroke
review_status: pending_domain_review
content_hash: "dummy"
---
Test body
"""
    # Fix the hash
    import json, hashlib
    payload = {
        "approval_metadata": {},
        "clinical_scope": "stroke",
        "content": "Test body",
        "date_reviewed": "2026-09-12",
        "id": "test-pending",
        "language": "en",
        "publication_date": "2026-05-01",
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "CDC",
        "source_url": "https://example.com",
        "terms": [],
        "title": "Test Pending",
        "version": "1.0",
    }
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    
    pending_content = pending_content.replace('"dummy"', h)
    
    p = tmp_path / "test.md"
    p.write_text(pending_content)
    
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0, "PENDING_DOMAIN_REVIEW must not be loaded"

def test_pending_safety_cannot_activate(tmp_path):
    import yaml
    data = {
        "patterns": [{
            "id": "p1",
            "pattern": "test",
            "description": "desc",
            "source": "src",
            "review_date": "2026-09-12",
            "review_status": "pending_domain_review"
        }]
    }
    p = tmp_path / "patterns.yaml"
    p.write_text(yaml.dump(data))
    
    patterns = load_patterns_dir(tmp_path)
    assert len(patterns) == 0, "PENDING_DOMAIN_REVIEW must not be loaded"

