import re

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'r') as f:
    c = f.read()

# Instead of fighting the test, let's just make the test use VoiceInput from hooks
# The mock needs to be applied to the correct path where Composer imports it
# Composer imports it from `../hooks/useVoiceInput`

c = c.replace(
    'vi.mock("../state/useVoiceInput"',
    'vi.mock("../hooks/useVoiceInput"'
)

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'w') as f:
    f.write(c)
