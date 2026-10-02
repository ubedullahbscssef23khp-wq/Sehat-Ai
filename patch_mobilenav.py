with open('frontend/src/components/MobileNav.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'onClick={() => { onNew(); onSetView(\'home\'); }}',
    'onClick={() => { onNew(); onSetView(\'home\'); }} aria-label={t.newConversation}'
)

with open('frontend/src/components/MobileNav.tsx', 'w') as f:
    f.write(content)
