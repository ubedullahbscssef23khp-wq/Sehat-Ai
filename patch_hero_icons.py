import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    'import { PulseIcon, InfoIcon, MenuIcon, CheckIcon, SparklesIcon, ActivityIcon, ShieldCheckIcon, StethoscopeIcon } from "./Icons";',
    'import { PulseIcon, InfoIcon, MenuIcon, SparklesIcon, ShieldCheckIcon } from "./Icons";'
)
c = c.replace('<PulseIcon size={28} color="#060913" />', '<PulseIcon size={28} />')
c = c.replace('<SparklesIcon size={16} color="var(--accent-teal)" />', '<SparklesIcon size={16} />')

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(c)

