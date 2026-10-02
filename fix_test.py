import re

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'r') as f:
    content = f.read()

# Fix the expectation of 1 button to 2 (Attach, Send)
content = content.replace(
    'expect(screen.getAllByRole("button").length).toBe(1);',
    'expect(screen.getAllByRole("button").length).toBe(2);'
)

# Fix the mic button click
content = content.replace(
    'const micBtn = screen.getAllByRole("button")[0];',
    'const micBtn = screen.getAllByRole("button")[1];'
)

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'w') as f:
    f.write(content)

