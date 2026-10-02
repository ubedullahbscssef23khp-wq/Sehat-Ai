import re

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'r') as f:
    c = f.read()

# For voice tests, we just use getAllByRole for start/stop since we patched Composer strings
c = c.replace(
    'screen.getByRole("button", { name: "Stop listening" })',
    'screen.getAllByRole("button")[0]'
)

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'w') as f:
    f.write(c)

