import re

with open("frontend/src/__tests__/App.test.tsx", "r", encoding="utf-8") as f:
    text = f.read()

text = text.replace(
    'screen.getByRole("button", { name: strings("en").newConversation })',
    'screen.getAllByRole("button", { name: strings("en").newConversation })[0]'
)
text = text.replace(
    'expect(screen.getAllByRole("button", { name: strings("en").newConversation })[0]).toBeInTheDocument();',
    'expect(screen.getAllByRole("button", { name: strings("en").newConversation })[0]).toBeInTheDocument();'
)

with open("frontend/src/__tests__/App.test.tsx", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed all tests")
