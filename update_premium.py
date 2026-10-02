import re

with open("frontend/src/styles/premium.css", "r", encoding="utf-8") as f:
    css = f.read()

css = re.sub(r'/\* Chat Overrides \*/.*?/\* Clinician Summary Premium \*/', '''/* Chat Overrides */
.message {
  margin-bottom: 32px;
}

.bubble.user-bubble {
  background: var(--accent-soft);
  color: var(--text-strong);
  border-radius: var(--radius-xl);
  border-bottom-right-radius: 4px;
  box-shadow: var(--shadow-sm);
  padding: 16px 20px;
  font-size: 1rem;
}
[dir="rtl"] .bubble.user-bubble {
  border-bottom-right-radius: var(--radius-xl);
  border-bottom-left-radius: 4px;
}

.card.assistant-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  border-top-left-radius: 4px;
  box-shadow: var(--shadow-sm);
  padding: 20px;
}
[dir="rtl"] .card.assistant-card {
  border-top-left-radius: var(--radius-xl);
  border-top-right-radius: 4px;
}

.assistant-card__text {
  font-size: 1.05rem;
  line-height: 1.6;
  color: var(--text-strong);
}

.message__avatar {
  background: var(--surface-hover);
  color: var(--accent);
  box-shadow: none;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  width: 40px;
  height: 40px;
}

/* Clinician Summary Premium */''', css, flags=re.DOTALL)

with open("frontend/src/styles/premium.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Updated premium.css")
