import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Add HandoffView to imports
content = content.replace(
    'import { HistoryView } from "./components/HistoryView";',
    'import { HistoryView } from "./components/HistoryView";\\nimport { HandoffView } from "./components/HandoffView";'
)

# Add "handoff" to AppView
content = content.replace(
    'type AppView = "home" | "chat" | "history";',
    'type AppView = "home" | "chat" | "history" | "handoff";'
)

# In handleDashboardAction, set view to handoff
content = content.replace(
    '''  const handleDashboardAction = useCallback((action: string) => {
    if (action === 'start') {
      // Nothing needed, user can just type
      if (composerRef.current) composerRef.current.focus();
    } else if (action === 'handoff') {
      // Show handoff? But how without a session? 
      // Maybe show history or a specific view?
    }
  }, []);''',
    '''  const handleDashboardAction = useCallback((action: string) => {
    if (action === 'start') {
      if (composerRef.current) composerRef.current.focus();
    } else if (action === 'handoff') {
      setView('handoff');
    }
  }, []);'''
)

# Add HandoffView to the rendering block
old_render = '''              {view === "chat" && (
                <ChatThread turns={chat.turns} busy={chat.busy} language={chat.language} />
              )}
            </div>'''
new_render = '''              {view === "chat" && (
                <ChatThread turns={chat.turns} busy={chat.busy} language={chat.language} />
              )}
              {view === "handoff" && (
                <HandoffView sessionId={chat.session?.id || null} language={chat.language} />
              )}
            </div>'''
content = content.replace(old_render, new_render)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
