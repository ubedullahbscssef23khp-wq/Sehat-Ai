import re

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'r') as f:
    c = f.read()

# Composer Voice tests try to click a mic button that uses state.useVoiceInput, which might be mocked incorrectly 
c = c.replace(
    'vi.mock("../state/useVoiceInput", () => ({',
    'vi.mock("../hooks/useVoiceInput", () => ({'
)

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'w') as f:
    f.write(c)

