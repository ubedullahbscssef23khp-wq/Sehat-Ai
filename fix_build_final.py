import re

# Fix fixtures signature
with open('frontend/src/__tests__/fixtures.ts', 'r') as f:
    c = f.read()

c = c.replace(
'''  structured_case: {
    chief_complaint: "Test",
    symptoms: [],
    demographics: {
      age_group: null,
      pregnant: null
    },
    red_flag_signals: []
  },''',
'''  structured_case: {
    chief_complaint: "Test",
    symptoms: [],
    demographics: {
      age_group: null,
      pregnant: null
    },
    red_flag_signals: [],
    associated_factors: [],
    missing_fields: [],
    confidence: "medium",
    raw_excerpt: ""
  },'''
)

with open('frontend/src/__tests__/fixtures.ts', 'w') as f:
    f.write(c)

# Fix localized parameters
files_to_patch = [
    'frontend/src/__tests__/DisclaimerBlock.test.tsx',
    'frontend/src/__tests__/EvidenceList.test.tsx',
    'frontend/src/__tests__/FollowUpList.test.tsx',
    'frontend/src/__tests__/TriageCard.test.tsx',
    'frontend/src/__tests__/AssistantMessage.test.tsx'
]

for file in files_to_patch:
    with open(file, 'r') as f:
        content = f.read()
    
    # We passed multiple arguments to syntheticLocalized but it only expects one
    content = re.sub(r'syntheticLocalized\("([^"]+)",\s*("[^"]+"),\s*("[^"]+")\)', r'syntheticLocalized("\1")', content)
    
    with open(file, 'w') as f:
        f.write(content)

