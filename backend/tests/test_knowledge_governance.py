import json
import hashlib
from datetime import date
from pathlib import Path
import pytest
from pydantic import ValidationError

from app.models import KnowledgeEntry, ReviewStatus
from app.knowledge.loader import KnowledgeLoadError, load_entries_dir, load_entry_file, parse_entry

def get_canonical_hash(payload: dict) -> str:
    canonical = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

def write_entry(directory: Path, name: str, review_status: str, content: str, mutate_hash: bool = False, omit_status: bool = False, omit_hash: bool = False, override_title=None, override_terms=None, override_source=None, override_date=None, original_hash=None) -> Path:
    eid = name.replace('.md', '')
    title = override_title if override_title is not None else f"Synthetic topic {name}"
    terms = override_terms if override_terms is not None else ["test"]
    source = override_source if override_source is not None else "synthetic source"
    date_rev = override_date if override_date is not None else "2026-01-15"
    
    payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": content.strip(),
        "date_reviewed": date_rev,
        "id": eid,
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": source,
        "source_url": None,
        "terms": terms,
        "title": title,
        "version": "1.0",
    }
    c_hash = original_hash if original_hash is not None else get_canonical_hash(payload)
    
    if mutate_hash:
        c_hash = "0" * 64
        
    status_line = f"review_status: {review_status}\n" if not omit_status else ""
    hash_line = f"content_hash: '{c_hash}'\n" if not omit_hash else ""
    
    # For terms in yaml
    terms_yaml = "[" + ", ".join(terms) + "]"
        
    text = f"""---
id: {eid}
title: {title}
terms: {terms_yaml}
source: {source}
date_reviewed: {date_rev}
{status_line}{hash_line}---
{content}"""
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path

def test_approved_entry_with_correct_hash_loads(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-app-1.md", "approved", "Valid content")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 1
    assert entries[0].id == "t-app-1"

def test_draft_entry_does_not_load(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-draft.md", "draft", "Draft content")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0

def test_pending_entry_does_not_load(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-pending.md", "pending_domain_review", "Pending content")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0

def test_rejected_entry_does_not_load(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-rejected.md", "rejected", "Rejected content")
    entries = load_entries_dir(tmp_path)
    assert len(entries) == 0

def test_approved_entry_with_incorrect_hash_fails_closed(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-badhash.md", "approved", "Valid content", mutate_hash=True)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

def test_missing_content_hash_fails(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-nohash.md", "approved", "Valid content", omit_hash=True)
    with pytest.raises(KnowledgeLoadError):
        load_entries_dir(tmp_path)

def test_missing_review_status_fails(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "t-nostatus.md", "approved", "Valid content", omit_status=True)
    with pytest.raises(KnowledgeLoadError):
        load_entries_dir(tmp_path)

# 2. changing body invalidates hash.
def test_changing_body_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-body-chg",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-body-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    write_entry(tmp_path, "t-body-chg.md", "approved", "Altered content", original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

# 3. changing terms invalidates hash.
def test_changing_terms_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-terms-chg",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-terms-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    write_entry(tmp_path, "t-terms-chg.md", "approved", "Valid content", override_terms=["test", "malicious"], original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

# 4. changing title invalidates hash.
def test_changing_title_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-title-chg",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-title-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    write_entry(tmp_path, "t-title-chg.md", "approved", "Valid content", override_title="Hacked title", original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

# 5. changing source invalidates hash.
def test_changing_source_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-src-chg",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-src-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    write_entry(tmp_path, "t-src-chg.md", "approved", "Valid content", override_source="Hacked source", original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

# 6. changing date_reviewed invalidates hash.
def test_changing_date_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-date-chg",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-date-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    write_entry(tmp_path, "t-date-chg.md", "approved", "Valid content", override_date="2026-01-16", original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)

# 8. changing review_status alone does NOT create a hash mismatch, but non-approved status is still excluded.
def test_changing_review_status_does_not_affect_hash(tmp_path: Path) -> None:
    # First verify it loads with approved
    write_entry(tmp_path, "t-status.md", "approved", "Valid content")
    assert len(load_entries_dir(tmp_path)) == 1
    # Now write the exact same entry but with draft, hash will be auto-calculated correctly (not containing status)
    write_entry(tmp_path, "t-status.md", "draft", "Valid content")
    # This proves the hash validates but the loader filters it!
    assert len(load_entries_dir(tmp_path)) == 0

# 11. Test deterministic canonicalization
def test_deterministic_canonicalization(tmp_path: Path) -> None:
    # Prove that the dictionary serialization is stable regardless of creation order
    payload_1 = {
        "title": "Test Title",
        "id": "test-id",
        "content": "Body text",
        "date_reviewed": "2026-01-01",
        "source": "CDC",
        "terms": ["alpha", "beta"],
        "approval_metadata": {},
        "clinical_scope": "general",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source_url": None,
        "version": "1.0",
    }
    payload_2 = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Body text",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source_url": None,
        "version": "1.0",
        "terms": ["alpha", "beta"],
        "source": "CDC",
        "date_reviewed": "2026-01-01",
        "id": "test-id",
        "title": "Test Title",
    }
    hash_1 = get_canonical_hash(payload_1)
    hash_2 = get_canonical_hash(payload_2)
    assert hash_1 == hash_2
    
    # Prove that semantic changes (like term ordering) change the hash.
    # While term order doesn't affect lexical retrieval, it is part of the canonical structure.
    payload_3 = payload_1.copy()
    payload_3["terms"] = ["beta", "alpha"]
    assert get_canonical_hash(payload_3) != hash_1


def test_duplicate_ids_fail(tmp_path: Path) -> None:
    write_entry(tmp_path, "entry1.md", "approved", "Valid content", override_title="Title1")
    # Duplicate ID via naming or override? The write_entry uses filename as ID.
    # We can create two files with same ID by writing manually.
    orig_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "dup-id",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic entry2",
        "version": "1.0",
    }
    h2 = get_canonical_hash(orig_payload)
    text2 = f"""---
id: dup-id
title: Synthetic topic entry2
terms: [test]
source: synthetic source
date_reviewed: 2026-01-15
review_status: approved
content_hash: \'{h2}\'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
Valid content"""
    (tmp_path / "entry2.md").write_text(text2, encoding="utf-8")
    
    orig_payload3 = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "dup-id",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic entry3",
        "version": "1.0",
    }
    h3 = get_canonical_hash(orig_payload3)
    text3 = f"""---
id: dup-id
title: Synthetic topic entry3
terms: [test]
source: synthetic source
date_reviewed: 2026-01-15
review_status: draft
content_hash: \'{h3}\'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
Valid content"""
    (tmp_path / "entry3.md").write_text(text3, encoding="utf-8")
    
    with pytest.raises(KnowledgeLoadError, match="duplicate entry id"):
        load_entries_dir(tmp_path)

def test_empty_content_fails(tmp_path: Path) -> None:
    path = write_entry(tmp_path, "empty.md", "approved", " ")
    with pytest.raises(KnowledgeLoadError, match="entry body must not be empty"):
        load_entries_dir(tmp_path)

def test_missing_source_fails(tmp_path: Path) -> None:
    text = f"""---
id: no-source
title: Title
terms: []
date_reviewed: 2026-01-15
review_status: approved
content_hash: \'123\'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
Body"""
    (tmp_path / "no-src.md").write_text(text)
    with pytest.raises(KnowledgeLoadError):
        load_entries_dir(tmp_path)

def test_missing_date_fails(tmp_path: Path) -> None:
    text = f"""---
id: no-date
title: Title
terms: []
source: Src
review_status: approved
content_hash: \'123\'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
Body"""
    (tmp_path / "no-date.md").write_text(text)
    with pytest.raises(KnowledgeLoadError):
        load_entries_dir(tmp_path)

# 7. changing id invalidates hash.
def test_changing_id_invalidates_hash(tmp_path: Path) -> None:
    original_payload = {
        "approval_metadata": {},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "t-id-orig",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title": "Synthetic topic t-id-chg.md",
        "version": "1.0",
    }
    orig_hash = get_canonical_hash(original_payload)
    # The new file has id: t-id-chg, which won't match orig_hash's id: t-id-orig
    write_entry(tmp_path, "t-id-chg.md", "approved", "Valid content", original_hash=orig_hash)
    with pytest.raises(KnowledgeLoadError, match="content hash mismatch"):
        load_entries_dir(tmp_path)
