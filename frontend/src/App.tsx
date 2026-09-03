import { useCallback, useEffect, useRef, useState } from "react";
import { fetchHealth } from "./api/health";
import { ChatThread } from "./components/ChatThread";
import { Composer } from "./components/Composer";
import { ErrorBanner } from "./components/ErrorBanner";
import { Hero } from "./components/Hero";
import { LanguagePicker } from "./components/LanguagePicker";
import { PlusIcon, PulseIcon } from "./components/Icons";
import { directionOf, strings } from "./i18n/strings";
import { useChat } from "./state/useChat";

type BackendStatus = "checking" | "online" | "offline";

export default function App() {
  const chat = useChat();
  const t = strings(chat.language);
  const dir = directionOf(chat.language);

  const [draft, setDraft] = useState("");
  const [backendStatus, setBackendStatus] = useState<BackendStatus>("checking");
  const composerRef = useRef<HTMLTextAreaElement>(null);

  const checkBackend = useCallback(() => {
    setBackendStatus("checking");
    fetchHealth()
      .then(() => setBackendStatus("online"))
      .catch(() => setBackendStatus("offline"));
  }, []);

  useEffect(() => {
    checkBackend();
  }, [checkBackend]);

  const handleSend = useCallback(
    (text: string) => {
      chat.send(text);
      setDraft("");
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
    composerRef.current?.focus();
  }, [chat]);

  const showOfflineBanner = backendStatus === "offline" && !chat.error;

  return (
    <div className="app" lang={chat.language} dir={dir}>
      <header className="topbar">
        <div className="wordmark">
          <span className="wordmark__icon" aria-hidden="true">
            <PulseIcon size={20} />
          </span>
          <span className="wordmark__name">{t.appName}</span>
        </div>

        <div className="topbar__controls">
          {chat.started && (
            <button
              type="button"
              className="ghost-button"
              onClick={handleNewConversation}
              disabled={chat.busy}
            >
              <PlusIcon size={15} />
              <span>{t.newConversation}</span>
            </button>
          )}
          <LanguagePicker language={chat.language} onChange={chat.setLanguage} disabled={chat.busy} />
        </div>
      </header>

      <main className="stage">
        <div className="stage__inner">
          {chat.started ? (
            <ChatThread turns={chat.turns} busy={chat.busy} language={chat.language} />
          ) : (
            <Hero language={chat.language} onStarter={handleStarter} />
          )}
        </div>
      </main>

      <div className="dock">
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
            disabled={chat.busy}
            onChange={setDraft}
            onSubmit={handleSend}
          />

          <p className="footnote">{t.disclaimerText}</p>
        </div>
      </div>
    </div>
  );
}
