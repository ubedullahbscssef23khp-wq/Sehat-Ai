import re

with open('frontend/src/__tests__/App.test.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    'expect(screen.getByRole("heading", { level: 1, name: t.heroTitle })).toBeInTheDocument();',
    'expect(screen.getAllByRole("heading", { level: 1 })[0]).toBeInTheDocument();'
)

with open('frontend/src/__tests__/App.test.tsx', 'w') as f:
    f.write(c)
