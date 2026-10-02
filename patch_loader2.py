import sys
import re
path = 'backend/tests/test_knowledge_loader.py'
content = open(path).read()

content = re.sub(r'VALID_FRONTMATTER = """\\.*?---.*?Synthetic curated body content."""', 
"""VALID_FRONTMATTER = \"\"\"\\
---
id: t-kb-1
title: Synthetic topic
terms: [synthetic-symptom, synthetic topic]
source: synthetic authoritative source
date_reviewed: 2026-01-15
review_status: approved
content_hash: 'b589657e716e84cf63ff72826479ec8d9b6feb6f7966b8d766f285c5782b8ba2'
language: en
reviewer_role: QUALIFIED_CLINICAL_REVIEWER
version: "1.0"
clinical_scope: general
---
Synthetic curated body content.\"\"\"""", content, flags=re.DOTALL)

open(path, 'w').write(content)
