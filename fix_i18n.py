import re

with open('frontend/src/i18n/strings.ts', 'r') as f:
    c = f.read()

c = c.replace(
'''export function strings(language: Language) {''',
'''export function strings(language: Language): any {'''
)

with open('frontend/src/i18n/strings.ts', 'w') as f:
    f.write(c)
