import re

# Fix fixtures signature
with open('frontend/src/__tests__/fixtures.ts', 'r') as f:
    c = f.read()

c = c.replace('confidence: "medium",', 'confidence: 2,')

with open('frontend/src/__tests__/fixtures.ts', 'w') as f:
    f.write(c)

with open('frontend/src/__tests__/EvidenceList.test.tsx', 'r') as f:
    content = f.read()

# We need to manually fix this one since the regex didn't catch it maybe due to whitespace
content = content.replace('syntheticLocalized("No matching guideline", "کوئی متعلقہ رہنما اصول نہیں ملا", "ڪو به لاڳاپيل ھدايت نه ملي")', 'syntheticLocalized("No matching guideline")')

with open('frontend/src/__tests__/EvidenceList.test.tsx', 'w') as f:
    f.write(content)

