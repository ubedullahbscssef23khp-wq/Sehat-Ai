with open('frontend/src/components/MobileNav.tsx', 'w') as f:
    f.write("""import { HomeIcon, PulseIcon, UserIcon, MenuIcon } from "./Icons";
import { strings } from "../i18n/strings";
import type { Language } from "../api/types";

interface Props {
  language: Language;
  onNew: () => void;
  busy: boolean;
  currentView: string;
  onSetView: (view: string) => void;
}

export function MobileNav({ language, onNew, busy, currentView, onSetView }: Props) {
  const t = strings(language);
  return (
    <nav className="mobile-nav mobile-only">
      <button 
        className={`mobile-nav__btn ${currentView === 'home' ? 'active' : ''}`} 
        onClick={() => { onNew(); onSetView('home'); }} 
        disabled={busy}
      >
        <HomeIcon size={24} />
        <span>Home</span>
      </button>
      <button 
        className={`mobile-nav__btn ${currentView === 'chat' ? 'active' : ''}`} 
        onClick={() => onSetView('chat')} 
        disabled={busy || currentView !== 'chat'}
      >
        <PulseIcon size={24} />
        <span>Assistant</span>
      </button>
      <button 
        className={`mobile-nav__btn ${currentView === 'history' ? 'active' : ''}`} 
        onClick={() => onSetView('history')} 
        disabled={busy}
      >
        <MenuIcon size={24} />
        <span>History</span>
      </button>
      <button className="mobile-nav__btn" disabled>
        <UserIcon size={24} />
        <span>Profile</span>
      </button>
    </nav>
  );
}
""")
