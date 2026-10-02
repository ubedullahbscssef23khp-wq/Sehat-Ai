import re

with open('frontend/src/components/ChatThread.tsx', 'r') as f:
    content = f.read()

# Replace user message styling
old_user_message = '''        turn.kind === "user" ? (
          <div key={turn.id} className="message message--user">
            <div className="bubble user-bubble" dir="auto" lang={language}>
              {turn.text}
            </div>
          </div>
        )'''

new_user_message = '''        turn.kind === "user" ? (
          <div key={turn.id} className="flex flex-col items-end mb-6 w-full" dir={language === 'ur' || language === 'sd' ? 'rtl' : 'ltr'}>
            <div className="max-w-[85%] md:max-w-[75%] px-5 py-3.5 bg-emerald-950/40 border border-emerald-500/20 backdrop-blur-xl rounded-2xl rounded-tr-sm shadow-[0_10px_20px_-10px_rgba(0,0,0,0.5)] text-emerald-50 text-[15px] leading-relaxed break-words" dir="auto" lang={language}>
              {turn.text}
            </div>
          </div>
        )'''

content = content.replace(old_user_message, new_user_message)

# Also remove className="thread" and use a basic Tailwind wrapper
content = content.replace('<div className="thread" role="log" aria-live="polite" aria-relevant="additions">', '<div className="w-full flex flex-col pb-8" role="log" aria-live="polite" aria-relevant="additions">')

with open('frontend/src/components/ChatThread.tsx', 'w') as f:
    f.write(content)
