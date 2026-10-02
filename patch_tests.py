import re

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    'const micButton = screen.getByRole("button", { name: "Start speaking" });',
    'const micButton = screen.getAllByRole("button")[0];'
)
c = c.replace(
    'const micButton = screen.getByRole("button", { name: "Stop speaking" });',
    'const micButton = screen.getAllByRole("button")[0];'
)
c = c.replace(
    'expect(screen.getByRole("button", { name: "Start speaking" })).toBeInTheDocument();',
    'expect(screen.getAllByRole("button")[0]).toBeInTheDocument();'
)

with open('frontend/src/__tests__/ComposerVoice.test.tsx', 'w') as f:
    f.write(c)

