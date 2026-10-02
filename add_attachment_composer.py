import re

with open('frontend/src/components/Composer.tsx', 'r') as f:
    content = f.read()

# Add PaperclipIcon to Icons.tsx if it doesn't exist, wait, let's just use an inline SVG for attachment
attachment_button = '''          <button
            type="button"
            className="flex-none w-10 h-10 mb-1 ml-1 rounded-full flex items-center justify-center text-slate-400 hover:text-white hover:bg-white/5 transition-all"
            disabled={disabled}
            title={t.attach || "Attach file"}
            aria-label={t.attach || "Attach file"}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
          </button>'''

# Currently:
# {isSupported && (
#    <button type="button" className={`flex-none w-10 h-10 ml-1 mb-1...

content = content.replace('{isSupported && (', attachment_button + '\\n          {isSupported && (')

with open('frontend/src/components/Composer.tsx', 'w') as f:
    f.write(content)

