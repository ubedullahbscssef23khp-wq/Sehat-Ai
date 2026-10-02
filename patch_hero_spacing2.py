import re

with open("frontend/src/styles/components.css", "r") as f:
    content = f.read()

# Reduce padding/margin in the hero to bring composer closer
content = re.sub(
    r'\.hero \{\s*display: flex;\s*flex-direction: column;\s*align-items: center;\s*text-align: center;\s*padding: 4rem 1rem 3rem;\s*\}',
    '.hero {\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  text-align: center;\n  padding: 2rem 1rem 1.5rem;\n}',
    content
)

with open("frontend/src/styles/components.css", "w") as f:
    f.write(content)
