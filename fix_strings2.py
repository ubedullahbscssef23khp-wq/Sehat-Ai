with open("frontend/src/i18n/strings.ts", "r") as f:
    content = f.read()

content += """
export function directionOf(language: Language): "ltr" | "rtl" {
  return language === "ur" || language === "sd" ? "rtl" : "ltr";
}
"""

replacements = [
    ('disclaimer: "This is a demonstration', 'disclaimer: "This is a demonstration",\n    disclaimerText: "This is a demonstration'),
    ('symptomsLabel: "Symptoms",', 'chiefComplaintLabel: "Chief Complaint",\n    triageDecisionLabel: "Triage Decision",\n    symptomsLabel: "Symptoms",'),
    ('symptomsLabel: "علامات",', 'chiefComplaintLabel: "بنیادی شکایت",\n    triageDecisionLabel: "ٹرائج کا فیصلہ",\n    symptomsLabel: "علامات",'),
    ('symptomsLabel: "علامتون",', 'chiefComplaintLabel: "مکيه شڪايت",\n    triageDecisionLabel: "ٽريج جو فيصلو",\n    symptomsLabel: "علامتون",')
]

for old, new in replacements:
    content = content.replace(old, new)

with open("frontend/src/i18n/strings.ts", "w") as f:
    f.write(content)
