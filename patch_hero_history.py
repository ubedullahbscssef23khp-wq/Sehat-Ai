import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'export function Hero({ language, onStarter, onAction, history, onLoadSession }: any)',
    'export function Hero({ language, onStarter, onAction, history, onLoadSession }: { language: "en"|"ur"|"sd", onStarter: any, onAction: any, history: any, onLoadSession: any })'
)
content = content.replace('import type { Language } from "../api/types";\n', '')

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)


with open('frontend/src/components/HistoryView.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'export function HistoryView({ language, history, onLoadSession, onDelete }: any)',
    'export function HistoryView({ language, history, onLoadSession, onDelete }: { language: "en"|"ur"|"sd", history: any, onLoadSession: any, onDelete: any })'
)
content = content.replace('import type { Language } from "../api/types";\n', '')

with open('frontend/src/components/HistoryView.tsx', 'w') as f:
    f.write(content)
