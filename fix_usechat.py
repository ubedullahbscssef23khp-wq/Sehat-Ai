import re

with open('frontend/src/state/useChat.ts', 'r') as f:
    content = f.read()

content = content.replace(
    'import { ApiError, NetworkError, createSession, getSessionHistory, sendMessage } from "../api/client";',
    'import { ApiError, NetworkError, getSessionHistory, v1SendMessage } from "../api/client";'
)

# Rewrite runSend
old_runSend = '''    try {
      let current = sessionRef.current;
      const isNew = current === null;
      if (current === null) {
        current = await createSession(languageRef.current);
        sessionRef.current = current;
        setSession(current);
      }
      
      if (onSessionUpdate) {
        onSessionUpdate(current.id, isNew ? text.slice(0, 60) : undefined);
      }
      
      const response = await sendMessage(current.id, text);'''

new_runSend = '''    try {
      let current = sessionRef.current;
      const isNew = current === null;
      const response = await v1SendMessage(text, current?.id, languageRef.current);
      
      if (isNew && !current) {
        // Mock a session structure if new, or wait for backend to provide it
        // The backend doesn't return the full session from v1SendMessage, it returns GuidanceResponse.
        // We can extract session_id from response
        const newSession = { id: response.session_id, preferred_language: languageRef.current, status: response.triage.level, created_at: new Date().toISOString() };
        sessionRef.current = newSession as any;
        setSession(newSession as any);
        current = newSession as any;
      }
      
      if (onSessionUpdate && current) {
        onSessionUpdate(current.id, isNew ? text.slice(0, 60) : undefined);
      }'''

content = content.replace(old_runSend, new_runSend)

with open('frontend/src/state/useChat.ts', 'w') as f:
    f.write(content)
