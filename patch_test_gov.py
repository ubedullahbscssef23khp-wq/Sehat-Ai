import sys
import re
path = 'backend/tests/test_knowledge_governance.py'
content = open(path).read()

old_payload = """    payload = {
        "content": content.strip(),
        "date_reviewed": date_rev,
        "id": eid,
        "source": source,
        "terms": terms,
        "title": title,
    }"""

new_payload = """    payload = {
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
    }"""
content = content.replace(old_payload, new_payload)

# also fix the text variables to include new fields when manually stringifying (dup-id, empty, no-source, no-date)

# Dup-id manual texts
old_h2_text = """    text2 = f"---\\n""id: dup-id\\n""title: Synthetic topic entry2\\n""terms: [test]\\n""source: synthetic source\\n""date_reviewed: 2026-01-15\\n""review_status: approved\\n""content_hash: '{h2}'\\n""---\\n""Valid content" """

# dup id replacements
content = re.sub(r'text2 = f"---\\n.*?Valid content"', 
    r'text2 = f"---\nid: dup-id\ntitle: Synthetic topic entry2\nterms: [test]\nsource: synthetic source\ndate_reviewed: 2026-01-15\nreview_status: approved\ncontent_hash: \'{h2}\'\nlanguage: en\nreviewer_role: QUALIFIED_CLINICAL_REVIEWER\nversion: 1.0\nclinical_scope: general\n---\nValid content"', 
    content, flags=re.DOTALL)

content = re.sub(r'text3 = f"---\\n.*?Valid content"', 
    r'text3 = f"---\nid: dup-id\ntitle: Synthetic topic entry3\nterms: [test]\nsource: synthetic source\ndate_reviewed: 2026-01-15\nreview_status: draft\ncontent_hash: \'{h3}\'\nlanguage: en\nreviewer_role: QUALIFIED_CLINICAL_REVIEWER\nversion: 1.0\nclinical_scope: general\n---\nValid content"', 
    content, flags=re.DOTALL)

# empty and no-source, no-date etc
# Note that no-src text uses an explicit string
content = re.sub(r'text = f"---\\n.*?Body"', 
    r'text = f"---\nid: no-source\ntitle: Title\nterms: []\ndate_reviewed: 2026-01-15\nreview_status: approved\ncontent_hash: \'123\'\nlanguage: en\nreviewer_role: QUALIFIED_CLINICAL_REVIEWER\nversion: 1.0\nclinical_scope: general\n---\nBody"', 
    content, count=1, flags=re.DOTALL)

# Next one is no-date.md text
content = re.sub(r'text = f"---\\n.*?Body"', 
    r'text = f"---\nid: no-date\ntitle: Title\nterms: []\nsource: Src\nreview_status: approved\ncontent_hash: \'123\'\nlanguage: en\nreviewer_role: QUALIFIED_CLINICAL_REVIEWER\nversion: 1.0\nclinical_scope: general\n---\nBody"', 
    content, count=1, flags=re.DOTALL)
    
# test_deterministic_canonicalization
# update payload_1 and payload_2
old_p1 = """    payload_1 = {
        "title": "Test Title",
        "id": "test-id",
        "content": "Body text",
        "date_reviewed": "2026-01-01",
        "source": "CDC",
        "terms": ["alpha", "beta"],
    }"""
new_p1 = """    payload_1 = {
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
    }"""
content = content.replace(old_p1, new_p1)

old_p2 = """    payload_2 = {
        "content": "Body text",
        "terms": ["alpha", "beta"],
        "source": "CDC",
        "date_reviewed": "2026-01-01",
        "id": "test-id",
        "title": "Test Title",
    }"""
new_p2 = """    payload_2 = {
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
    }"""
content = content.replace(old_p2, new_p2)

# Fix test_changing_body_invalidates_hash and similar hardcoded payloads
for f_name in ['t-body-chg', 't-terms-chg', 't-title-chg', 't-src-chg', 't-date-chg', 't-id-orig']:
    o_str = f"""    original_payload = {{
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "{f_name}",
        "source": "synthetic source",
        "terms": ["test"],
        "title":"""
        
    n_str = f"""    original_payload = {{
        "approval_metadata": {{}},
        "clinical_scope": "general",
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "{f_name}",
        "language": "en",
        "publication_date": None,
        "reviewer_role": "QUALIFIED_CLINICAL_REVIEWER",
        "source": "synthetic source",
        "source_url": None,
        "terms": ["test"],
        "title":"""
        
    n_str += f""" "Synthetic topic {f_name.replace('-orig', '-chg')}.md",\n        "version": "1.0",\n    }}""" if f_name == 't-id-orig' else f""" "Synthetic topic {f_name}.md",\n        "version": "1.0",\n    }}"""
    
    # We will use regex for safety on the title matching
    content = re.sub(
        r'original_payload = \{\s*"content": "Valid content",\s*"date_reviewed": "2026-01-15",\s*"id": "' + f_name + r'",\s*"source": "synthetic source",\s*"terms": \["test"\],\s*"title":.*?\n    \}',
        n_str,
        content, flags=re.DOTALL
    )

old_dup_payload = """    orig_payload = {
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "dup-id",
        "source": "synthetic source",
        "terms": ["test"],
        "title": "Synthetic topic entry2",
    }"""
new_dup_payload = """    orig_payload = {
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
    }"""
content = content.replace(old_dup_payload, new_dup_payload)

old_dup3_payload = """    orig_payload3 = {
        "content": "Valid content",
        "date_reviewed": "2026-01-15",
        "id": "dup-id",
        "source": "synthetic source",
        "terms": ["test"],
        "title": "Synthetic topic entry3",
    }"""
new_dup3_payload = """    orig_payload3 = {
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
    }"""
content = content.replace(old_dup3_payload, new_dup3_payload)

open(path, 'w').write(content)
