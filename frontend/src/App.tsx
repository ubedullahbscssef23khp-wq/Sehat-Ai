import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHealth } from "./api/health";
import { ChatThread } from "./components/ChatThread";
import { Composer } from "./components/Composer";
import { ErrorBanner } from "./components/ErrorBanner";
import { Hero } from "./components/Hero";
import { LanguagePicker } from "./components/LanguagePicker";
import { PulseIcon, UserIcon, HomeIcon, MenuIcon, ShieldCheckIcon } from "./components/Icons";
import { directionOf, strings } from "./i18n/strings";
import { useChat } from "./state/useChat";
import { useHistory } from "./state/useHistory";
import { HistoryView } from "./components/HistoryView";
import { HandoffView } from "./components/HandoffView";

type BackendStatus = "checking" | "online" | "offline";
type AppView = "home" | "chat" | "history" | "handoff";

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
      if (chat.started) {
         setView('chat');
      }
    }
  }, [chat.started]);
  
  const showOfflineBanner = backendStatus === "offline" && !chat.error;
  
  return (
    <div 
      lang={chat.language} 
      dir={dir}
      className="fixed inset-0 w-full h-full bg-[#060913] text-white overflow-hidden flex flex-col font-sans"
    >
      {/* AMBIENT SPATIAL DEPTH BLURS */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
        <div className="absolute -top-1/4 -left-1/4 w-[150%] h-[150%]" style={{ background: 'radial-gradient(circle at 18% 12%, rgba(37, 99, 235, 0.22) 0%, transparent 45%)' }}></div>
        <div className="absolute -bottom-1/4 -right-1/4 w-[150%] h-[150%]" style={{ background: 'radial-gradient(circle at 82% 85%, rgba(6, 182, 212, 0.15) 0%, transparent 45%)' }}></div>
      </div>

      <div className="flex flex-col h-full relative z-10 w-full max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
        
        {/* HEADER CARD */}
        <header className="flex-none mt-4 md:mt-6 mb-6">
          <div className="bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-3xl shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)] px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-3 cursor-pointer" onClick={handleNewConversation}>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center text-white shadow-[0_0_20px_rgba(6,182,212,0.4)]">
                <PulseIcon size={22} />
              </div>
              <div className="flex flex-col">
                <span className="font-extrabold text-lg tracking-tight leading-tight">{t.appName || "Sehat AI"}</span>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="text-[0.65rem] uppercase tracking-wider text-emerald-400/90 font-medium font-mono">Verified Clinical Core</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <div className="hidden sm:block">
                 <LanguagePicker language={chat.language} onChange={chat.setLanguage} disabled={chat.busy} />
              </div>
              <button className="hidden md:flex w-10 h-10 rounded-full bg-white/5 border border-white/10 items-center justify-center hover:bg-white/10 transition-colors" aria-label="Profile">
                <UserIcon size={18} />
              </button>
            </div>
          </div>
        </header>

        {/* RESPONSIVE CONTAINER & SHELL ARCHITECTURE */}
        <div className="flex-1 min-h-0 flex flex-col md:flex-row gap-6 mb-20 md:mb-6 relative">
          
          {/* DESKTOP SIDEBAR */}
          <aside className="hidden md:flex flex-col w-64 bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)] p-4">
            <nav className="flex flex-col gap-2 flex-1">
              <button 
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${view === 'home' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.15)]' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}
                onClick={() => { handleNewConversation(); setView('home'); }} aria-label={t.newConversation}
                disabled={chat.busy}
              >
                <HomeIcon size={18} /> {t.newConversation}
              </button>
              <button 
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${view === 'chat' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.15)]' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}
                onClick={() => setView('chat')}
                disabled={chat.busy || view !== 'chat'}
              >
                <PulseIcon size={18} /> Active Session
              </button>
              <button 
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium ${view === 'history' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20 shadow-[0_0_15px_rgba(37,99,235,0.15)]' : 'text-slate-300 hover:bg-white/5 hover:text-white'}`}
                onClick={() => setView('history')}
                disabled={chat.busy}
              >
                <MenuIcon size={18} /> History
              </button>
            </nav>
            <div className="mt-auto px-4 py-3 bg-white/5 rounded-xl border border-white/10">
              <p className="text-[10px] text-slate-400 text-center uppercase tracking-widest font-semibold mb-1">Assist, don't diagnose</p>
              <div className="flex items-center justify-center gap-1.5 mt-2 pt-2 border-t border-white/10">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                <span className="text-[10px] text-cyan-300/80 font-mono tracking-wider">CLINICAL MODE: DETERMINISTIC</span>
              </div>
            </div>
          </aside>

          {/* MAIN CONTENT AREA */}
          <main className="flex-1 flex flex-col min-h-0 bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)] overflow-hidden relative">
            <div className="flex-1 overflow-y-auto p-4 md:p-8 no-scrollbar">
              {view === "home" && (
                <Hero 
                  language={chat.language} 
                  onStarter={handleStarter} 
                  onAction={handleDashboardAction}
                />
              )}
              {view === "history" && (
                <HistoryView language={chat.language} history={history} onLoadSession={handleLoadSession} onDelete={remove} />
              )}
              {view === "chat" && (
                <ChatThread turns={chat.turns} busy={chat.busy} language={chat.language} />
              )}
              {view === "handoff" && (
                <HandoffView sessionId={chat.session?.id || null} language={chat.language} />
              )}
            </div>

            {/* DOCKED COMPOSER FOR DESKTOP AND CHAT VIEW */}
            {(view === "home" || view === "chat") && (
              <div className="flex-none p-4 md:p-6 bg-gradient-to-t from-[#060913] to-transparent pointer-events-none">
                <div className="pointer-events-auto max-w-3xl mx-auto">
                  {chat.error && (
                    <div className="mb-4">
                      <ErrorBanner
                        error={chat.error}
                        language={chat.language}
                        onRetry={chat.retry}
                        onNewConversation={handleNewConversation}
                      />
                    </div>
                  )}
                  {showOfflineBanner && (
                    <div className="mb-4 bg-rose-500/20 border border-rose-500/30 rounded-2xl p-4 flex justify-between items-center backdrop-blur-xl">
                      <span className="text-rose-200 text-sm font-medium">{t.errorOffline}</span>
                      <button className="px-4 py-1.5 bg-rose-500 hover:bg-rose-600 rounded-lg text-white text-sm font-medium transition-colors" onClick={checkBackend}>
                        {t.retry}
                      </button>
                    </div>
                  )}
                  
                  <div className="relative">
                    <Composer
                      ref={composerRef}
                      language={chat.language}
                      value={draft}
                      disabled={chat.busy || chat.session?.status === "closed"}
                      onChange={setDraft}
                      onSubmit={handleSend}
                    />
                  </div>

                </div>
              </div>
            )}
          </main>
        </div>

        {/* MOBILE BOTTOM NAV */}
        <nav className="md:hidden fixed bottom-6 left-4 right-4 bg-[#0f172a]/90 backdrop-blur-xl border border-white/10 rounded-full shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)] p-2 flex justify-around items-center z-50">
          <button 
            className={`flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all relative ${view === 'home' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            onClick={() => { handleNewConversation(); setView('home'); }} aria-label={t.newConversation}
            disabled={chat.busy}
          >
            <HomeIcon size={22} />
            {view === 'home' && <span className="absolute bottom-1 w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>}
          </button>
          <button 
            className={`flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all relative ${view === 'chat' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            onClick={() => setView('chat')}
            disabled={chat.busy || view !== 'chat'}
          >
            <PulseIcon size={22} />
            {view === 'chat' && <span className="absolute bottom-1 w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>}
          </button>
          <button 
            className={`flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all relative ${view === 'history' ? 'text-cyan-400' : 'text-slate-400 hover:text-white'}`}
            onClick={() => setView('history')}
            disabled={chat.busy}
          >
            <MenuIcon size={22} />
            {view === 'history' && <span className="absolute bottom-1 w-1 h-1 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>}
          </button>
          <button className="flex flex-col items-center justify-center w-12 h-12 rounded-full transition-all relative text-slate-400 hover:text-white" disabled>
            <ShieldCheckIcon size={22} />
          </button>
        </nav>
      </div>
    </div>
  );
}
