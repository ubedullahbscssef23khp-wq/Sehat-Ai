with open('frontend/src/components/Hero.tsx', 'r') as f:
    c = f.read()
c = c.replace(
    'export function Hero({ language, onStarter, onAction, history, onLoadSession }: { language: "en"|"ur"|"sd", onStarter: any, onAction: any, history: any, onLoadSession: any }) {',
    'export function Hero({ language, onStarter, onAction }: { language: "en"|"ur"|"sd", onStarter: any, onAction: any }) {'
)
with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(c)

with open('frontend/src/App.tsx', 'r') as f:
    c = f.read()
c = c.replace(
    'history={history}\n                  onLoadSession={handleLoadSession}',
    ''
)
with open('frontend/src/App.tsx', 'w') as f:
    f.write(c)
