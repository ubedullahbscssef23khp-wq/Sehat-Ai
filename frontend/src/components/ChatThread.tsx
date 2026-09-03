import { useEffect, useRef } from "react";
import type { Language } from "../api/types";
import type { Turn } from "../state/useChat";
import { AssistantMessage } from "./AssistantMessage";
import { ThinkingIndicator } from "./ThinkingIndicator";

interface ChatThreadProps {
  turns: Turn[];
  busy: boolean;
  language: Language;
}

export function ChatThread({ turns, busy, language }: ChatThreadProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const target = bottomRef.current;
    if (!target) return;
    const reduce =
      typeof window.matchMedia === "function" &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "end" });
  }, [turns.length, busy]);

  return (
    <div className="thread" role="log" aria-live="polite" aria-relevant="additions">
      {turns.map((turn) =>
        turn.kind === "user" ? (
          <div key={turn.id} className="message message--user">
            <div className="bubble user-bubble" dir="auto" lang={language}>
              {turn.text}
            </div>
          </div>
        ) : (
          <AssistantMessage key={turn.id} response={turn.response} language={language} />
        ),
      )}
      {busy && <ThinkingIndicator language={language} />}
      <div ref={bottomRef} />
    </div>
  );
}
