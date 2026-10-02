import re

with open("frontend/src/styles/components.css", "r") as f:
    content = f.read()

# Make hero subtitle responsive to container
content = re.sub(
    r'\.hero__subtitle \{\s*margin: 0 auto;\s*max-width: 34rem;\s*color: var\(--text-muted\);\s*font-size: 1\.02rem;\s*\}',
    '.hero__subtitle {\n  margin: 0 auto;\n  max-width: 34rem;\n  color: var(--text-muted);\n  font-size: 1.02rem;\n  margin-bottom: 0.5rem;\n}',
    content
)

with open("frontend/src/styles/components.css", "w") as f:
    f.write(content)
