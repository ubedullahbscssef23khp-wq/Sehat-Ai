import sys
import re
path = 'backend/tests/conversation_support.py'
content = open(path).read()

old_payload = """        "content": content,
        "date_reviewed": "2026-01-01",
        "id": entry_id,
        "source": SYNTHETIC_SOURCE,
        "terms": list(terms),
        "title": f"Synthetic topic {entry_id}","""

new_payload = """        "approval_metadata": {},
        "clinical_scope": "general",
        "content": content,
        "date_reviewed": "2026-01-01",
        "id": entry_id,
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": SYNTHETIC_SOURCE,
        "source_url": None,
        "terms": list(terms),
        "title": f"Synthetic topic {entry_id}",
        "version": "1.0","""

content = content.replace(old_payload, new_payload)

old_return = """    return KnowledgeEntry(
        id=entry_id,
        title=f"Synthetic topic {entry_id}",
        terms=list(terms),
        content=content,
        source=SYNTHETIC_SOURCE,
        date_reviewed="2026-01-01", # type: ignore
        review_status=ReviewStatus.APPROVED,
        content_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
    )"""

new_return = """    return KnowledgeEntry(
        id=entry_id,
        title=f"Synthetic topic {entry_id}",
        terms=list(terms),
        content=content,
        source=SYNTHETIC_SOURCE,
        date_reviewed="2026-01-01", # type: ignore
        review_status=ReviewStatus.APPROVED,
        content_hash=hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        language="en", # type: ignore
        reviewer_role="QUALIFIED_CLINICAL_REVIEWER",
        version="1.0",
        clinical_scope="general",
        approval_metadata={}
    )"""
content = content.replace(old_return, new_return)
open(path, 'w').write(content)
