with open('frontend/src/components/Composer.tsx', 'r') as f:
    c = f.read()
c = c.replace(
    'title={isListening ? t.stopVoice : t.startVoice}',
    'title={isListening ? t.stopVoice : t.startVoice} aria-label={isListening ? t.stopVoice : t.startVoice}'
)
with open('frontend/src/components/Composer.tsx', 'w') as f:
    f.write(c)
