with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

content = content.replace(
    'import { PulseIcon, UserIcon, MenuIcon, CloseIcon } from "./components/Icons";',
    'import { PulseIcon, UserIcon } from "./components/Icons";'
)

content = content.replace(
    'import { HistoryDrawer } from "./components/HistoryDrawer";\n',
    ''
)

content = content.replace(
    '<MobileNav \n        language={chat.language} \n        onNew={handleNewConversation} \n        busy={chat.busy} \n        currentView={view}\n        onSetView={setView}\n      />',
    '<MobileNav \n        language={chat.language} \n        onNew={handleNewConversation} \n        busy={chat.busy} \n        currentView={view}\n        onSetView={(v: string) => setView(v as AppView)}\n      />'
)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
