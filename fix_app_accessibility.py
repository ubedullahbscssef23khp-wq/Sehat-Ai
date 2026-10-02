import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Fix desktop home button
content = content.replace("onClick={() => { handleNewConversation(); setView('home'); }}", "onClick={() => { handleNewConversation(); setView('home'); }} aria-label={t.newConversation}")

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)

