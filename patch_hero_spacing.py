import re

with open("frontend/src/styles/components.css", "r") as f:
    content = f.read()

# Reduce padding/margin in the hero to bring composer closer
content = content.replace(
    ".hero {\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  text-align: center;\n  padding: 4rem 1rem 3rem;\n}",
    ".hero {\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  text-align: center;\n  padding: 2rem 1rem 1.5rem;\n}"
)

content = content.replace(
    ".hero__title {\n  font-size: 2.25rem;\n  font-weight: 600;\n  line-height: 1.2;\n  color: var(--text-strong);\n  letter-spacing: -0.02em;\n  margin-bottom: 1.25rem;\n  max-width: 600px;\n}",
    ".hero__title {\n  font-size: 2.25rem;\n  font-weight: 600;\n  line-height: 1.2;\n  color: var(--text-strong);\n  letter-spacing: -0.02em;\n  margin-bottom: 0.75rem;\n  max-width: 600px;\n}"
)

with open("frontend/src/styles/components.css", "w") as f:
    f.write(content)
