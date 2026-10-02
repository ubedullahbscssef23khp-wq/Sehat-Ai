import sys
path = 'backend/tests/test_knowledge_loader.py'
content = open(path).read()

old_fm = """VALID_FRONTMATTER = \"\"\"\\
---
id: t-kb-1
title: Synthetic topic
terms: [synthetic-symptom, synthetic topic]
source: synthetic authoritative source
date_reviewed: 2026-01-15
review_status: approved
content_hash: '9e229482f01f0297d82d85a9a01501c9a89884fc98a4a527ead21c5a542a45b2'
---
Synthetic curated body content.\"\"\""""

new_fm = """VALID_FRONTMATTER = \"\"\"\\
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
Synthetic curated body content.\"\"\""""

content = content.replace(old_fm, new_fm)
content = content.replace("f0c72f413013da7bd634746679ea774d0d0c7739cfc9f6120bc9d8703bfb6dbf", "af3257f4357d528dceb1d29451ffab5d989bfc8141cbf626564287b7bfd22df8")
open(path, 'w').write(content)
