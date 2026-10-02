import re

with open("frontend/src/i18n/strings.ts", "r") as f:
    content = f.read()

# Add missing properties to STRINGS based on what TS is complaining about
replacements = [
    ('evidenceHeading: "Medical Evidence"', 'evidenceHeading: "Medical Evidence",\n    evidence: "Medical Evidence",\n    evidenceNote: "No specific guideline matched this query.",\n    evidenceSource: "Source"'),
    ('followUpHeading: "Follow-up Questions"', 'followUpHeading: "Follow-up Questions",\n    followUp: "Follow-up Questions"'),
    ('assistantName: "Assistant"', 'assistantName: "Assistant",\n    assistant: "Assistant"'),
    ('voiceInputUnsupported: "Voice input unavailable on this browser/language."', 'voiceInputUnsupported: "Voice input unavailable on this browser/language.",\n    voiceUnsupported: "Voice input unavailable on this browser/language."'),
    ('startSpeaking: "Start speaking"', 'startSpeaking: "Start speaking",\n    voiceStart: "Start speaking"'),
    ('stopListening: "Stop listening"', 'stopListening: "Stop listening",\n    voiceStop: "Stop listening"'),
    ('pulseListening: "Listening..."', 'pulseListening: "Listening...",\n    voiceListening: "Listening..."'),
    ('sendButton: "Send"', 'sendButton: "Send",\n    send: "Send"'),
    ('disclaimer: "This is a demonstration. This tool does not provide medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions."', 'disclaimer: "This is a demonstration. This tool does not provide medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions.",\n    disclaimerHeading: "Disclaimer"'),
    ('retryButton: "Retry"', 'retryButton: "Retry",\n    retry: "Retry"'),
    ('offlineError: "Unable to connect. Please check your internet connection and try again."', 'offlineError: "Unable to connect. Please check your internet connection and try again.",\n    errorOffline: "Unable to connect. Please check your internet connection and try again.",\n    errorServer: "Server error",\n    errorValidation: "Validation error",\n    errorTooLong: "Message too long",\n    errorClosed: "Connection closed",\n    errorNotFound: "Not found",\n    errorUnavailable: "Service unavailable",\n    errorGeneric: "An error occurred"')
]

for old, new in replacements:
    content = content.replace(old, new)

# Duplicate for UR
replacements_ur = [
    ('evidenceHeading: "طبی شواہد"', 'evidenceHeading: "طبی شواہد",\n    evidence: "طبی شواہد",\n    evidenceNote: "اس سوال سے کوئی مخصوص ہدایت نامہ میل نہیں کھاتا۔",\n    evidenceSource: "ذریعہ"'),
    ('followUpHeading: "مزید سوالات"', 'followUpHeading: "مزید سوالات",\n    followUp: "مزید سوالات"'),
    ('assistantName: "معاون"', 'assistantName: "معاون",\n    assistant: "معاون"'),
    ('voiceInputUnsupported: "اس براؤزر/زبان پر صوتی ان پٹ دستیاب نہیں ہے۔"', 'voiceInputUnsupported: "اس براؤزر/زبان پر صوتی ان پٹ دستیاب نہیں ہے۔",\n    voiceUnsupported: "اس براؤزر/زبان پر صوتی ان پٹ دستیاب نہیں ہے۔"'),
    ('startSpeaking: "بولنا شروع کریں"', 'startSpeaking: "بولنا شروع کریں",\n    voiceStart: "بولنا شروع کریں"'),
    ('stopListening: "سننا بند کریں"', 'stopListening: "سننا بند کریں",\n    voiceStop: "سننا بند کریں"'),
    ('pulseListening: "سن رہا ہے..."', 'pulseListening: "سن رہا ہے...",\n    voiceListening: "سن رہا ہے..."'),
    ('sendButton: "بھیجیں"', 'sendButton: "بھیجیں",\n    send: "بھیجیں"'),
    ('disclaimer: "یہ ایک نمائشی ٹول ہے۔ یہ ٹول طبی مشورہ، تشخیص یا علاج فراہم نہیں کرتا۔ طبی فیصلوں کے لیے ہمیشہ کسی مستند ڈاکٹر سے رجوع کریں۔"', 'disclaimer: "یہ ایک نمائشی ٹول ہے۔ یہ ٹول طبی مشورہ، تشخیص یا علاج فراہم نہیں کرتا۔ طبی فیصلوں کے لیے ہمیشہ کسی مستند ڈاکٹر سے رجوع کریں۔",\n    disclaimerHeading: "دستبرداری"'),
    ('retryButton: "دوبارہ کوشش کریں"', 'retryButton: "دوبارہ کوشش کریں",\n    retry: "دوبارہ کوشش کریں"'),
    ('offlineError: "منسلک ہونے سے قاصر۔ براہ کرم اپنا انٹرنیٹ کنکشن چیک کریں اور دوبارہ کوشش کریں۔"', 'offlineError: "منسلک ہونے سے قاصر۔ براہ کرم اپنا انٹرنیٹ کنکشن چیک کریں اور دوبارہ کوشش کریں۔",\n    errorOffline: "منسلک ہونے سے قاصر۔ براہ کرم اپنا انٹرنیٹ کنکشن چیک کریں اور دوبارہ کوشش کریں۔",\n    errorServer: "سرور کی خرابی",\n    errorValidation: "توثیق کی خرابی",\n    errorTooLong: "پیغام بہت طویل ہے",\n    errorClosed: "رابطہ منقطع ہو گیا",\n    errorNotFound: "نہیں ملا",\n    errorUnavailable: "سروس دستیاب نہیں",\n    errorGeneric: "ایک خرابی پیش آ گئی"')
]
for old, new in replacements_ur:
    content = content.replace(old, new)


# Duplicate for SD
replacements_sd = [
    ('evidenceHeading: "طبي ثبوت"', 'evidenceHeading: "طبي ثبوت",\n    evidence: "طبي ثبوت",\n    evidenceNote: "هن سوال سان ڪو به مخصوص هدايت نامو نٿو ملي.",\n    evidenceSource: "ذريعو"'),
    ('followUpHeading: "وڌيڪ سوال"', 'followUpHeading: "وڌيڪ سوال",\n    followUp: "وڌيڪ سوال"'),
    ('assistantName: "مددگار"', 'assistantName: "مددگار",\n    assistant: "مددگار"'),
    ('voiceInputUnsupported: "هن برائوزر/ٻولي تي آواز جو ان پٽ دستياب ناهي."', 'voiceInputUnsupported: "هن برائوزر/ٻولي تي آواز جو ان پٽ دستياب ناهي.",\n    voiceUnsupported: "هن برائوزر/ٻولي تي آواز جو ان پٽ دستياب ناهي."'),
    ('startSpeaking: "ڳالهائڻ شروع ڪريو"', 'startSpeaking: "ڳالهائڻ شروع ڪريو",\n    voiceStart: "ڳالهائڻ شروع ڪريو"'),
    ('stopListening: "ٻڌڻ بند ڪريو"', 'stopListening: "ٻڌڻ بند ڪريو",\n    voiceStop: "ٻڌڻ بند ڪريو"'),
    ('pulseListening: "ٻڌي رهيو آهي..."', 'pulseListening: "ٻڌي رهيو آهي...",\n    voiceListening: "ٻڌي رهيو آهي..."'),
    ('sendButton: "موڪليو"', 'sendButton: "موڪليو",\n    send: "موڪليو"'),
    ('disclaimer: "هي هڪ نمائش آهي. هي اوزار طبي مشورو، تشخيص يا علاج مهيا نٿو ڪري. طبي فيصلن لاءِ هميشه ڪنهن قابل ڊاڪٽر سان صلاح ڪريو."', 'disclaimer: "هي هڪ نمائش آهي. هي اوزار طبي مشورو، تشخيص يا علاج مهيا نٿو ڪري. طبي فيصلن لاءِ هميشه ڪنهن قابل ڊاڪٽر سان صلاح ڪريو.",\n    disclaimerHeading: "دستبرداري"'),
    ('retryButton: "ٻيهر ڪوشش ڪريو"', 'retryButton: "ٻيهر ڪوشش ڪريو",\n    retry: "ٻيهر ڪوشش ڪريو"'),
    ('offlineError: "ڳنڍڻ کان قاصر. مھرباني ڪري پنھنجو انٽرنيٽ ڪنيڪشن چيڪ ڪريو ۽ ٻيھر ڪوشش ڪريو."', 'offlineError: "ڳنڍڻ کان قاصر. مھرباني ڪري پنھنجو انٽرنيٽ ڪنيڪشن چيڪ ڪريو ۽ ٻيھر ڪوشش ڪريو.",\n    errorOffline: "ڳنڍڻ کان قاصر. مھرباني ڪري پنھنجو انٽرنيٽ ڪنيڪشن چيڪ ڪريو ۽ ٻيھر ڪوشش ڪريو.",\n    errorServer: "سرور جي خرابي",\n    errorValidation: "تصديق جي خرابي",\n    errorTooLong: "پيغام تمام ڊگهو آهي",\n    errorClosed: "رابطو ختم ٿي ويو",\n    errorNotFound: "نه مليو",\n    errorUnavailable: "سروس دستياب ناهي",\n    errorGeneric: "هڪ خرابي ٿي پئي"')
]
for old, new in replacements_sd:
    content = content.replace(old, new)


with open("frontend/src/i18n/strings.ts", "w") as f:
    f.write(content)
