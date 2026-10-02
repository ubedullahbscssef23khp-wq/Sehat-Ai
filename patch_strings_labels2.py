import re

with open("frontend/src/i18n/strings.ts", "r") as f:
    content = f.read()

# Add remaining missing labels
replacements_en = [
    ('symptomsLabel: "Symptoms",', 'clinicianSummaryHeading: "Clinician Summary",\n    clinicianSummaryBadge: "Auto-generated",\n    symptomsLabel: "Symptoms",')
]

for old, new in replacements_en:
    content = content.replace(old, new, 1)

replacements_ur = [
    ('symptomsLabel: "علامات",', 'clinicianSummaryHeading: "طبی خلاصہ",\n    clinicianSummaryBadge: "خودکار طور پر تیار کردہ",\n    symptomsLabel: "علامات",')
]
for old, new in replacements_ur:
    content = content.replace(old, new, 1)

replacements_sd = [
    ('symptomsLabel: "علامتون",', 'clinicianSummaryHeading: "ڊاڪٽر جو خلاصو",\n    clinicianSummaryBadge: "خودڪار تيار ٿيل",\n    symptomsLabel: "علامتون",')
]
for old, new in replacements_sd:
    content = content.replace(old, new, 1)


with open("frontend/src/i18n/strings.ts", "w") as f:
    f.write(content)
