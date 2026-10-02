import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    c = f.read()

c = c.replace('const t = strings(language) as any;\n', '')
c = c.replace('import { strings } from "../i18n/strings";\n', '')

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(c)

