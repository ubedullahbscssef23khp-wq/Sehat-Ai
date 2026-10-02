with open('frontend/src/components/Sidebar.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'onClick={() => { onNew(); onSetView(\'home\'); }}',
    'onClick={() => { onNew(); onSetView(\'home\'); }} aria-label={t.newConversation}'
)

content = content.replace(
    'aria-label={t.newConversation}',
    '',
    1
)

with open('frontend/src/components/Sidebar.tsx', 'w') as f:
    f.write(content)
