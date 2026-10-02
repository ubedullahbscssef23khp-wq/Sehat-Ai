import os
import re

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Update strings.ts
strings_path = 'frontend/src/i18n/strings.ts'
with open(strings_path, 'r', encoding='utf-8') as f:
    strings_content = f.read()

# Make heroTitle more premium, and add quick action strings
strings_content = strings_content.replace(
    'heroTitle: "What can I help you with today?",',
    'heroTitle: "Hello, how can SehatAI help you today?",\n    actionStart: "Start conversation",\n    actionHistory: "View history",\n    actionHandoff: "Clinician handoff",'
)
strings_content = strings_content.replace(
    'heroTitle: "آج میں آپ کی کیا مدد کر سکتا ہوں؟",',
    'heroTitle: "آج میں آپ کی کیا مدد کر سکتا ہوں؟",\n    actionStart: "بات چیت شروع کریں",\n    actionHistory: "تاریخ دیکھیں",\n    actionHandoff: "ڈاکٹر کی رپورٹ",'
)
strings_content = strings_content.replace(
    'heroTitle: "اڄ مان توهان جي ڪهڙي مدد ڪري سگهان ٿو؟",',
    'heroTitle: "اڄ مان توهان جي ڪهڙي مدد ڪري سگهان ٿو؟",\n    actionStart: "ڳالهه ٻولهه شروع ڪريو",\n    actionHistory: "تاريخ ڏسو",\n    actionHandoff: "ڊاڪٽر جي رپورٽ",'
)
write_file(strings_path, strings_content)


print("Created Python script")
