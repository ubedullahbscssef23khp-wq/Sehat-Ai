import re

with open("frontend/src/components/Sidebar.tsx", "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace('export function Sidebar({ onNew, busy }: any) {', 'import { strings } from "../i18n/strings";\n\nexport function Sidebar({ language, onNew, busy }: any) {\n  const t = strings(language);')
text = text.replace('<span>SehatAI Assistant</span>', '<span>{t.newConversation}</span>')
text = text.replace('<button className="sidebar__nav-item active" onClick={onNew} disabled={busy}>', '<button className="sidebar__nav-item active" onClick={onNew} disabled={busy} aria-label={t.newConversation}>')
with open("frontend/src/components/Sidebar.tsx", "w", encoding="utf-8") as f:
    f.write(text)

with open("frontend/src/components/MobileNav.tsx", "r", encoding="utf-8") as f:
    text = f.read()
text = text.replace('export function MobileNav({ language, onNew, busy, onSelectSession, isHome, onHome }: any) {', 'import { strings } from "../i18n/strings";\n\nexport function MobileNav({ language, onNew, busy, onSelectSession, isHome, onHome }: any) {\n  const t = strings(language);')
text = text.replace('<button className={`mobile-nav__btn ${!isHome ? \'active\' : \'\'}`} onClick={onNew} disabled={busy}>', '<button className={`mobile-nav__btn ${!isHome ? \'active\' : \'\'}`} onClick={onNew} disabled={busy} aria-label={t.newConversation}>')
with open("frontend/src/components/MobileNav.tsx", "w", encoding="utf-8") as f:
    f.write(text)

print("Fixed buttons")
