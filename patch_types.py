import re

with open('frontend/src/i18n/strings.ts', 'r') as f:
    c = f.read()

# Add missing types in i18n
c = c.replace('clinicianSummaryLabel: "Clinician Summary",', 'clinicianSummaryLabel: "Clinician Summary",\n    copySBAR: "Copy SBAR",\n    print: "Print",\n    chiefComplaint: "Chief Complaint",\n    symptoms: "Symptoms",\n    timeline: "Timeline",\n    composerLabel: "Composer",\n    stopVoice: "Stop speaking",\n    startVoice: "Start speaking",')
c = c.replace('clinicianSummaryLabel: "کلینیکل خلاصہ",', 'clinicianSummaryLabel: "کلینیکل خلاصہ",\n    copySBAR: "SBAR کاپی کریں",\n    print: "پرنٹ",\n    chiefComplaint: "بنیادی شکایت",\n    symptoms: "علامات",\n    timeline: "ٹائم لائن",\n    composerLabel: "پیغام",\n    stopVoice: "بولنا بند کریں",\n    startVoice: "بولنا شروع کریں",')
c = c.replace('clinicianSummaryLabel: "ڪلينڪل خلاصو",', 'clinicianSummaryLabel: "ڪلينڪل خلاصو",\n    copySBAR: "SBAR نقل ڪريو",\n    print: "پرنٽ",\n    chiefComplaint: "بنيادي شڪايت",\n    symptoms: "علامتون",\n    timeline: "ٽائم لائن",\n    composerLabel: "پيغام",\n    stopVoice: "ڳالهائڻ بند ڪريو",\n    startVoice: "ڳالهائڻ شروع ڪريو",')

with open('frontend/src/i18n/strings.ts', 'w') as f:
    f.write(c)
