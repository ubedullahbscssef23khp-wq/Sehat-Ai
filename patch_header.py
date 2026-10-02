with open('frontend/src/App.tsx', 'r') as f:
    c = f.read()

c = c.replace(
'''      <header className="global-header">
        <div className="global-header__brand" onClick={handleNewConversation} style={{ cursor: 'pointer' }}>
          <PulseIcon size={24} />
          <span>{t.appName || "SehatAI"}</span>
        </div>''',
'''      <header className="global-header">
        <div className="global-header__brand" onClick={handleNewConversation} style={{ cursor: 'pointer' }}>
          <div style={{width: 36, height: 36, borderRadius: 12, background: 'linear-gradient(to top right, var(--accent-teal), var(--accent))', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', boxShadow: 'var(--shadow-glow-cyan)'}}>
             <PulseIcon size={20} />
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
             <span>{t.appName || "SehatAI"}</span>
             <span className="brand-badge">GPT-4o Medical / Active</span>
          </div>
        </div>'''
)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(c)
