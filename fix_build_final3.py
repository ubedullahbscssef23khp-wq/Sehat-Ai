import re

with open('frontend/src/__tests__/EvidenceList.test.tsx', 'r') as f:
    content = f.read()

content = re.sub(r'syntheticLocalized\(\s*"No matching guideline"[^\)]+\)', r'syntheticLocalized("No matching guideline")', content)

with open('frontend/src/__tests__/EvidenceList.test.tsx', 'w') as f:
    f.write(content)

