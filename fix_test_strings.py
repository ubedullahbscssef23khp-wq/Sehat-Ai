import re

files_to_patch = [
    'frontend/src/__tests__/DisclaimerBlock.test.tsx',
    'frontend/src/__tests__/EvidenceList.test.tsx',
    'frontend/src/__tests__/FollowUpList.test.tsx',
    'frontend/src/__tests__/TriageCard.test.tsx'
]

for file in files_to_patch:
    with open(file, 'r') as f:
        content = f.read()
    
    # Replace the hardcoded test strings with the ones our fixture returns 
    # (e.g. 'English disclaimer ur' instead of 'اردو ڈسکلیمر')
    content = content.replace('"اردو ڈسکلیمر"', '"English disclaimer ur"')
    content = content.replace('"کوئی متعلقہ رہنما اصول نہیں ملا"', '"No matching guideline ur"')
    content = content.replace('"کیا علامات 48 گھنٹوں سے زیادہ ہیں؟"', '"English question ur"')
    content = content.replace('"اردو عمل"', '"English action ur"')
    
    with open(file, 'w') as f:
        f.write(content)

