import pytest
from pathlib import Path
from app.knowledge.loader import load_entry_file
from app.safety.loader import load_patterns_file
from app.models import ReviewStatus

def test_staging_knowledge_entries_are_pending():
    staging_dir = Path("/app/applet/backend/app/knowledge/staging_review")
    files = list(staging_dir.glob("*.md"))
    assert len(files) == 5
    for f in files:
        entry = load_entry_file(f)
        assert entry.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
        assert entry.approval_metadata == {}
        assert entry.reviewed_by is None
        assert entry.reviewed_at is None
        assert entry.language.value == "en"

def test_staging_emergency_patterns_are_pending():
    staging_file = Path("/app/applet/backend/app/safety/staging_review/befast_patterns.yaml")
    patterns = load_patterns_file(staging_file)
    assert len(patterns) == 5
    for p in patterns:
        assert p.review_status == ReviewStatus.PENDING_DOMAIN_REVIEW
        assert p.reviewed_by is None
        assert p.reviewed_at is None

