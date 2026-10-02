import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Let's write a new App.tsx that implements the layout properly
new_content = """import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHealth } from "./api/health";
import { ChatThread } from "./components/ChatThread";
import { Composer } from "./components/Composer";
import { ErrorBanner } from "./components/ErrorBanner";
import { Hero } from "./components/Hero";
import { LanguagePicker } from "./components/LanguagePicker";
import { PulseIcon, UserIcon, MenuIcon, CloseIcon } from "./components/Icons";
import { directionOf, strings } from "./i18n/strings";
import { useChat } from "./state/useChat";
import { useHistory } from "./state/useHistory";
import { Sidebar } from "./components/Sidebar";
import { MobileNav } from "./components/MobileNav";
import { HistoryDrawer } from "./components/HistoryDrawer";
import { HistoryView } from "./components/HistoryView";

type BackendStatus = "checking" | "online" | "offline";
type AppView = "home" | "chat" | "history";

export default function App() {
  const { history, addOrUpdate, remove } = useHistory();
  const chat = useChat("en", addOrUpdate);
  const t = strings(chat.language) as any;
  const dir = directionOf(chat.language);
  
  const [draft, setDraft] = useState("");
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");
  const composerRef = useRef<HTMLTextAreaElement>(null);
  const [view, setView] = useState<AppView>("home");
  
  const checkBackend = useCallback(() => {
    setBackendStatus("checking");
    fetchHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);
  
  useEffect(() => {
    checkBackend();
  }, [checkBackend]);
  
  useEffect(() => {
    if (chat.started && view === "home") {
      setView("chat");
    }
  }, [chat.started, view]);

  const handleSend = useCallback(
    (text: string) => {
      chat.send(text);
      setDraft("");
      setView("chat");
    },
    [chat],
  );
  
  const handleStarter = useCallback((text: string) => {
    setDraft(text);
    composerRef.current?.focus();
  }, []);
  
  const handleNewConversation = useCallback(() => {
    chat.reset();
    setDraft("");
    setView("home");
    setTimeout(() => {
      composerRef.current?.focus();
    }, 100);
  }, [chat]);

  const handleLoadSession = useCallback((id: string) => {
    chat.loadSession(id);
    setView("chat");
  }, [chat]);

  const handleDashboardAction = useCallback((action: string) => {
    if (action === 'start') {
      composerRef.current?.focus();
    } else if (action === 'history') {
      setView('history');
    } else if (action === 'handoff') {
      // Typically handoff requires an active session
      if (chat.started) {
         setView('chat');
      }
    }
  }, [chat.started]);
  
  const showOfflineBanner = backendStatus === "offline" && !chat.error;
  
  return (
    <div className="app premium-app" lang={chat.language} dir={dir}>
      {/* GLOBAL TOP HEADER */}
      <header className="global-header">
        <div className="global-header__brand" onClick={handleNewConversation} style={{ cursor: 'pointer' }}>
          <PulseIcon size={24} />
          <span>{t.appName || "SehatAI"}</span>
        </div>
        <div className="global-header__controls">
          <LanguagePicker language={chat.language} onChange={chat.setLanguage} disabled={chat.busy} />
          <button className="ghost-button desktop-only" aria-label="Profile">
             <UserIcon size={18} />
          </button>
        </div>
      </header>

      <div className="premium-workspace">
        <Sidebar 
          language={chat.language} 
          onNew={handleNewConversation} 
          busy={chat.busy} 
          currentView={view}
          onSetView={setView}
        />
        
        <div className="main-content">
          <div className="main-scroll-area">
            <div className={view === "home" ? "dashboard-container" : "chat-container"}>
              {view === "home" && (
                <Hero 
                  language={chat.language} 
                  onStarter={handleStarter} 
                  onAction={handleDashboardAction}
                  history={history}
                  onLoadSession={handleLoadSession}
                />
              )}
              {view === "history" && (
                <HistoryView 
                  language={chat.language}
                  history={history}
                  onLoadSession={handleLoadSession}
                  onDelete={remove}
                />
              )}
              {view === "chat" && (
                <ChatThread turns={chat.turns} busy={chat.busy} language={chat.language} />
              )}
            </div>
          </div>
          
          {(view === "home" || view === "chat") && (
            <div className="dock premium-dock">
              <div className="dock__inner">
                {chat.error && (
                  <ErrorBanner
                    error={chat.error}
                    language={chat.language}
                    onRetry={chat.retry}
                    onNewConversation={handleNewConversation}
                  />
                )}
                {showOfflineBanner && (
                  <div className="error-banner" role="alert">
                    <p className="error-banner__text">
                      <span>{t.errorOffline}</span>
                    </p>
                    <button type="button" className="error-banner__action" onClick={checkBackend}>
                      <span>{t.retry}</span>
                    </button>
                  </div>
                )}
                
                <Composer
                  ref={composerRef}
                  language={chat.language}
                  value={draft}
                  disabled={chat.busy || chat.session?.status === "closed"}
                  onChange={setDraft}
                  onSubmit={handleSend}
                />
                <p className="footnote">
                  {t.disclaimerText} <br />
                  <span className="governance-notice">Clinical activation is gated by qualified human clinical review.</span>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      <MobileNav 
        language={chat.language} 
        onNew={handleNewConversation} 
        busy={chat.busy} 
        currentView={view}
        onSetView={setView}
      />
    </div>
  );
}
"""

with open('frontend/src/App.tsx', 'w') as f:
    f.write(new_content)

print("Updated App.tsx")
