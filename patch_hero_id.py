with open('frontend/src/components/Hero.tsx', 'r') as f:
    c = f.read()
c = c.replace(
    '<h1>{t.appName || "SehatAI"}</h1>',
    '<h1 id="hero-title">{t.appName || "SehatAI"}</h1>'
)
with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(c)
