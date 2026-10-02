import re

with open('frontend/src/i18n/strings.ts', 'r') as f:
    c = f.read()

# Add the types properly to avoid TS errors
c = c.replace(
'''export function strings(language: Language): any {''',
'''export function strings(language: Language): any {'''
)
# It's already any but the error still shows up? Wait, the return type is checked based on the assignment type. No, TypeScript is complaining that the properties don't exist on the union type of what strings() returns.
# That means strings() return type inference is failing despite `: any`.

with open('frontend/src/i18n/strings.ts', 'w') as f:
    f.write(c)
