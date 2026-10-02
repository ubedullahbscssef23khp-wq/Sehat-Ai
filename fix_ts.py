import re

# App.test.tsx
with open('frontend/src/__tests__/App.test.tsx', 'r') as f:
    content = f.read()
content = re.sub(r'const mockSession1 = .*?\n', '', content)
content = re.sub(r'const mockSession2 = .*?\n', '', content)
content = re.sub(r'const mockSession = .*?\n', '', content)
with open('frontend/src/__tests__/App.test.tsx', 'w') as f:
    f.write(content)

# HandoffView.tsx
with open('frontend/src/components/HandoffView.tsx', 'r') as f:
    content = f.read()
content = content.replace('const t = strings(language);', '')
content = content.replace('import { strings } from "../i18n/strings";', '')
with open('frontend/src/components/HandoffView.tsx', 'w') as f:
    f.write(content)

# useHistory.ts
with open('frontend/src/state/useHistory.ts', 'r') as f:
    content = f.read()
content = content.replace(', SessionListItem ', ' ')
with open('frontend/src/state/useHistory.ts', 'w') as f:
    f.write(content)

