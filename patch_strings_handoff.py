with open("frontend/src/i18n/strings.ts", "r") as f:
    content = f.read()

replacements = [
    (
        'clinicianSummaryBadge: "Auto-generated",',
        'clinicianSummaryBadge: "Auto-generated",\n    copyHandoff: "Copy Handoff",\n    printHandoff: "Print",\n    copySuccess: "Copied!",\n    handoffTitle: "SEHATAI — CLINICIAN HANDOFF",\n    handoffDisclaimer1: "AI-assisted structured summary",\n    handoffDisclaimer2: "Verify information before clinical use.",\n    handoffFooter: "Important:\\nThis summary assists clinical communication and does not replace\\nprofessional clinical judgment.",\n    generatedLabel: "Generated",\n    modelAttributionLabel: "Model Attribution",\n    notProvided: "Not provided",'
    ),
    (
        'clinicianSummaryBadge: "خودکار طور پر تیار کردہ",',
        'clinicianSummaryBadge: "خودکار طور پر تیار کردہ",\n    copyHandoff: "نقل کریں",\n    printHandoff: "پرنٹ کریں",\n    copySuccess: "نقل ہو گیا!",\n    handoffTitle: "SEHATAI — CLINICIAN HANDOFF",\n    handoffDisclaimer1: "اے آئی کی مدد سے تیار کردہ ساختہ خلاصہ",\n    handoffDisclaimer2: "طبی استعمال سے پہلے معلومات کی تصدیق کریں۔",\n    handoffFooter: "اہم:\\nیہ خلاصہ طبی مواصلات میں مدد کرتا ہے اور پیشہ ورانہ طبی فیصلے کا متبادل نہیں ہے۔",\n    generatedLabel: "تیار کردہ",\n    modelAttributionLabel: "ماڈل انتساب",\n    notProvided: "فراہم نہیں کیا گیا",'
    ),
    (
        'clinicianSummaryBadge: "خودڪار تيار ٿيل",',
        'clinicianSummaryBadge: "خودڪار تيار ٿيل",\n    copyHandoff: "نقل ڪريو",\n    printHandoff: "پرنٽ ڪريو",\n    copySuccess: "نقل ٿي ويو!",\n    handoffTitle: "SEHATAI — CLINICIAN HANDOFF",\n    handoffDisclaimer1: "اي آءِ جي مدد سان تيار ڪيل خلاصو",\n    handoffDisclaimer2: "طبي استعمال کان اڳ معلومات جي تصديق ڪريو.",\n    handoffFooter: "اهم:\\nهي خلاصو طبي رابطي ۾ مدد ڪري ٿو ۽ پيشه ورانه طبي فيصلي جو متبادل ناهي.",\n    generatedLabel: "تيار ڪيل",\n    modelAttributionLabel: "ماڊل انتساب",\n    notProvided: "مهيا نه ڪيو ويو",'
    )
]

for old, new in replacements:
    content = content.replace(old, new)

with open("frontend/src/i18n/strings.ts", "w") as f:
    f.write(content)
