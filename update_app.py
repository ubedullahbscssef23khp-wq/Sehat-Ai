import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

content = content.replace("radial-gradient(circle at 15% 15%, rgba(37, 99, 235, 0.22) 0%, transparent 45%)", "radial-gradient(circle at 18% 12%, rgba(37, 99, 235, 0.22) 0%, transparent 45%)")
content = content.replace("radial-gradient(circle at 85% 75%, rgba(6, 182, 212, 0.15) 0%, transparent 45%)", "radial-gradient(circle at 82% 85%, rgba(6, 182, 212, 0.15) 0%, transparent 45%)")

# We need to make sure the quick prompts are matching the expected 2-column or 3-card grid (I did this in Hero.tsx already)
# Also need to make sure header capsule matches.

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
