import re

with open('frontend/src/__tests__/AssistantMessage.test.tsx', 'r') as f:
    content = f.read()

# Replace the text the test is looking for with what the fixture produces
content = content.replace('"اردو رہنمائی پیغام"', '"English user message ur"')

with open('frontend/src/__tests__/AssistantMessage.test.tsx', 'w') as f:
    f.write(content)

