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
    <div className="w-full flex flex-col pb-8" role="log" aria-live="polite" aria-relevant="additions">
      {turns.map((turn) =>
        turn.kind === "user" ? (
          <div key={turn.id} className="flex flex-col items-end mb-6 w-full" dir={language === 'ur' || language === 'sd' ? 'rtl' : 'ltr'}>
            <div className="max-w-[85%] md:max-w-[75%] px-5 py-3.5 bg-emerald-950/40 border border-emerald-500/20 backdrop-blur-xl rounded-2xl rounded-tr-sm shadow-[0_10px_20px_-10px_rgba(0,0,0,0.5)] text-emerald-50 text-[15px] leading-relaxed break-words" dir="auto" lang={language}>
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
