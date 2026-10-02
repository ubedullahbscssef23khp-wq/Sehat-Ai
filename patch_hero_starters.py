with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

starter_block = """
      <div className="hero__starters" style={{ marginTop: '32px' }}>
        <h3 className="section-title" style={{ fontSize: '1.1rem', marginBottom: '16px' }}>Or try asking...</h3>
        <div className="hero__starter-grid premium-starter-grid">
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt.key}
              type="button"
              className="starter-chip premium-chip"
              onClick={(e) => {
                e.stopPropagation();
                onStarter(prompt.text[language]);
              }}
            >
              {prompt.text[language]}
            </button>
          ))}
        </div>
      </div>
"""

content = content.replace(
    '<div className="dashboard-grid">',
    starter_block + '\n      <div className="dashboard-grid" style={{ marginTop: "32px" }}>'
)

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)
