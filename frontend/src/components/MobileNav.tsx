import { HomeIcon, PulseIcon, UserIcon, MenuIcon } from "./Icons";
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
        onClick={() => { onNew(); onSetView('home'); }} aria-label={t.newConversation}
        disabled={busy}
      >
        <HomeIcon size={20} />
      </button>
      <button 
        className={`mobile-nav__btn ${currentView === 'chat' ? 'active' : ''}`}
        onClick={() => onSetView('chat')}
        disabled={busy || currentView !== 'chat'}
      >
        <PulseIcon size={20} />
      </button>
      <button 
        className={`mobile-nav__btn ${currentView === 'history' ? 'active' : ''}`}
        onClick={() => onSetView('history')}
        disabled={busy}
      >
        <MenuIcon size={20} />
      </button>
      <button className="mobile-nav__btn" disabled>
        <UserIcon size={20} />
      </button>
    </nav>
  );
}
