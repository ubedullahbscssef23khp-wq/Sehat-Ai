import sys
import re
path = "backend/app/safety/signals.py"
with open(path, "r") as f:
    text = f.read()

text = re.sub(
    r"_ALLOWED_SIGNALS: set\[str\] = \{[^}]+\}",
    "_ALLOWED_SIGNALS: set[str] = set()",
    text
)

with open(path, "w") as f:
    f.write(text)
print("patched signals.py")
