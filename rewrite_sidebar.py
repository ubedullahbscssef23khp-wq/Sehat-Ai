with open('frontend/src/components/Sidebar.tsx', 'w') as f:
    f.write("""import { PulseIcon, HomeIcon, UserIcon, MenuIcon } from "./Icons";
import { strings } from "../i18n/strings";

export function Sidebar({ language, onNew, busy, currentView, onSetView }: any) {
  const t = strings(language);
  return (
    <aside className="sidebar desktop-only">
      <nav className="sidebar__nav">
        <button 
          className={`sidebar__nav-item ${currentView === 'home' ? 'active' : ''}`} 
          onClick={() => { onNew(); onSetView('home'); }} 
          disabled={busy}
        >
          <HomeIcon size={18} />
          <span>Home</span>
        </button>
        <button 
          className={`sidebar__nav-item ${currentView === 'chat' ? 'active' : ''}`} 
          onClick={() => onSetView('chat')} 
          disabled={busy || currentView !== 'chat'}
          aria-label={t.newConversation}
        >
          <PulseIcon size={18} />
          <span>Assistant</span>
        </button>
        <button 
          className={`sidebar__nav-item ${currentView === 'history' ? 'active' : ''}`} 
          onClick={() => onSetView('history')} 
          disabled={busy}
        >
          <MenuIcon size={18} />
          <span>History</span>
        </button>
        <button className="sidebar__nav-item" disabled>
          <UserIcon size={18} />
          <span>Profile & Settings</span>
        </button>
      </nav>
      <div className="sidebar__footer">
        <div className="sidebar__badge">Assist, don't diagnose.</div>
      </div>
    </aside>
  );
}
""")
