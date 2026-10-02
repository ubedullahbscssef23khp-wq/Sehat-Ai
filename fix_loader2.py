import re
path = 'backend/tests/test_knowledge_loader.py'
content = open(path).read()

content = content.replace("content_hash: '9e229482f01f0297d82d85a9a01501c9a89884fc98a4a527ead21c5a542a45b2'", 
"content_hash: 'b589657e716e84cf63ff72826479ec8d9b6feb6f7966b8d766f285c5782b8ba2'\nlanguage: en\nreviewer_role: QUALIFIED_CLINICAL_REVIEWER\nversion: \"1.0\"\nclinical_scope: general")

open(path, 'w').write(content)
