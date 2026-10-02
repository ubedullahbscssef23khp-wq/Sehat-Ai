with open("frontend/src/components/Sidebar.tsx", "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace('export function Sidebar({ onNew, busy }: any) {', 'export function Sidebar({ language, onNew, busy }: any) {')
with open("frontend/src/components/Sidebar.tsx", "w", encoding="utf-8") as f:
    f.write(text)
