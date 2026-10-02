import re

with open("frontend/src/styles/components.css", "r") as f:
    content = f.read()

# Reduce padding/margin in the hero to bring composer closer
content = re.sub(
    r'\.hero \{\s*max-width: 40rem;\s*margin: 6vh auto 0;\s*text-align: center;\s*padding: 24px 8px;\s*animation: rise var\(--dur-slow\) var\(--ease\) both;\s*\}',
    '.hero {\n  max-width: 40rem;\n  margin: 3vh auto 0;\n  text-align: center;\n  padding: 12px 8px;\n  animation: rise var(--dur-slow) var(--ease) both;\n}',
    content
)

content = re.sub(
    r'\.hero__starters \{\s*margin-top: 30px;\s*\}',
    '.hero__starters {\n  margin-top: 20px;\n}',
    content
)

content = re.sub(
    r'\.hero__safety \{\s*display: flex;\s*align-items: flex-start;\s*justify-content: center;\s*gap: 8px;\s*margin: 34px auto 0;\s*max-width: 38rem;\s*text-align: left;\s*color: var\(--text-faint\);\s*font-size: 0\.85rem;\s*line-height: 1\.5;\s*\}',
    '.hero__safety {\n  display: flex;\n  align-items: flex-start;\n  justify-content: center;\n  gap: 8px;\n  margin: 20px auto 0;\n  max-width: 38rem;\n  text-align: left;\n  color: var(--text-faint);\n  font-size: 0.85rem;\n  line-height: 1.5;\n}',
    content
)

with open("frontend/src/styles/components.css", "w") as f:
    f.write(content)
