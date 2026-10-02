import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Remove the disclaimer from App.tsx
old_disclaimer = '''                  <p className="text-center text-xs text-slate-500 mt-3 font-medium">
                    {t.disclaimerText} <span className="opacity-70">| Clinical activation gated by review.</span>
                  </p>'''

content = content.replace(old_disclaimer, '')

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
