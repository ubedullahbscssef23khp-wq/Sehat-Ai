import re

with open("frontend/src/i18n/strings.ts", "r") as f:
    content = f.read()

# Add clinician summary fields missing from TS
replacements_en = [
    ('triageLabels: {', 'symptomsLabel: "Symptoms",\n    severityLabel: "Severity",\n    durationLabel: "Duration",\n    progressionLabel: "Progression",\n    demographicsLabel: "Demographics",\n    ageGroupLabel: "Age Group",\n    pregnancyLabel: "Pregnancy",\n    pregnantYes: "Pregnant",\n    pregnantNo: "Not pregnant",\n    redFlagsLabel: "Red Flags",\n    firedRulesLabel: "Fired Rules",\n    timelineLabel: "Timeline",\n    triageLabels: {')
]

for old, new in replacements_en:
    content = content.replace(old, new, 1)

replacements_ur = [
    ('triageLabels: {', 'symptomsLabel: "علامات",\n    severityLabel: "شدت",\n    durationLabel: "دورانیہ",\n    progressionLabel: "ترقی",\n    demographicsLabel: "آبادیات",\n    ageGroupLabel: "عمر کا گروپ",\n    pregnancyLabel: "حمل",\n    pregnantYes: "حاملہ",\n    pregnantNo: "حاملہ نہیں",\n    redFlagsLabel: "خطرے کی علامات",\n    firedRulesLabel: "لاگو قوانین",\n    timelineLabel: "ٹائم لائن",\n    triageLabels: {')
]
for old, new in replacements_ur:
    content = content.replace(old, new, 1)

replacements_sd = [
    ('triageLabels: {', 'symptomsLabel: "علامتون",\n    severityLabel: "شدت",\n    durationLabel: "مدو",\n    progressionLabel: "ترقي",\n    demographicsLabel: "آبادي جي ڄاڻ",\n    ageGroupLabel: "عمر جو گروپ",\n    pregnancyLabel: "حمل",\n    pregnantYes: "حامله",\n    pregnantNo: "حامله ناهي",\n    redFlagsLabel: "خطري جون نشانيون",\n    firedRulesLabel: "لاڳو ٿيل قاعدا",\n    timelineLabel: "ٽائيم لائن",\n    triageLabels: {')
]
for old, new in replacements_sd:
    content = content.replace(old, new, 1)


with open("frontend/src/i18n/strings.ts", "w") as f:
    f.write(content)
