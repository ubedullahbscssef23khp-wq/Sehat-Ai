import sys
import re
path = 'backend/tests/test_knowledge_governance.py'
content = open(path).read()

# Replace any textX = f"--- with textX = f\"\"\"---
content = re.sub(r'(text\w*\s*=\s*)f"---', r'\1f\"\"\"---', content)
content = re.sub(r'---(\\n)?\nBody"', r'---\nBody\"\"\"', content)
content = re.sub(r'---(\\n)?\nValid content"', r'---\nValid content\"\"\"', content)
open(path, 'w').write(content)
