/** Lightweight chat store built on React state only.
 *
 * The store orchestrates the API conversation; it never computes triage, risk,
 * or medical content. Everything medical arrives from the backend and is kept
 * verbatim in `GuidanceResponse`. No health text is persisted to storage or
 * logged to the console.
 */

import { useCallback, useRef, useState } from "react";
import { ApiError, NetworkError, getSessionHistory, v1SendMessage } from "../api/client";
import type { GuidanceResponse, Language, Session } from "../api/types";

export type Turn =
  | { kind: "user"; id: string; text: string; at: number }
  | { kind: "assistant"; id: string; response: GuidanceResponse; at: number };

/** A UI-level error classification mapped onto friendly strings in i18n. */
export type UiErrorKind =
  | "offline"
  | "server"
  | "validation"
  | "tooLong"
  | "closed"
  | "notFound"
  | "unavailable"
  | "generic";

export interface UiError {
  kind: UiErrorKind;
}

let turnCounter = 0;
function nextId(prefix: string): string {
  turnCounter += 1;
  return `${prefix}-${turnCounter}`;
}

function classify(error: unknown): UiError {
  if (error instanceof NetworkError) {
    return { kind: "offline" };
  }
  if (error instanceof ApiError) {
    switch (error.code) {
      case "message_empty":
      case "validation_error":
        return { kind: "validation" };
      case "message_too_long":
        return { kind: "tooLong" };
      case "session_closed":
        return { kind: "closed" };
      case "session_not_found":
        return { kind: "notFound" };
      case "llm_unavailable":
        return { kind: "unavailable" };
      default:
        return { kind: error.status >= 500 ? "server" : "generic" };
    }
  }
  return { kind: "generic" };
}

export interface ChatStore {
  language: Language;
  session: Session | null;
  turns: Turn[];
  busy: boolean;
  error: UiError | null;
  started: boolean;
  send: (text: string) => void;
  retry: () => void;
  reset: () => void;
  setLanguage: (language: Language) => void;
  loadSession: (session_id: string) => Promise<void>;
}

export function useChat(
  initialLanguage: Language = "en",
  onSessionUpdate?: (id: string, preview?: string) => void
): ChatStore {
  const [language, setLanguageState] = useState<Language>(initialLanguage);
  const [session, setSession] = useState<Session | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<UiError | null>(null);

  // Refs so retry() can re-run the last attempt without stale closures.
  const sessionRef = useRef<Session | null>(null);
  const languageRef = useRef<Language>(initialLanguage);
  const lastAttemptRef = useRef<string>("");
  const busyRef = useRef(false);

  sessionRef.current = session;
  languageRef.current = language;

  const runSend = useCallback(async (text: string) => {
    busyRef.current = true;
    setBusy(true);
    setError(null);
    lastAttemptRef.current = text;

    try {
      let current = sessionRef.current;
      const isNew = current === null;
      const response = await v1SendMessage(text, current?.id, languageRef.current);
      
      if (isNew && !current) {
        // Mock a session structure if new, or wait for backend to provide it
        // The backend doesn't return the full session from v1SendMessage, it returns GuidanceResponse.
        // We can extract session_id from response
        const newSession = { id: response.session_id, preferred_language: languageRef.current, status: response.triage.level, created_at: new Date().toISOString() };
        sessionRef.current = newSession as any;
        setSession(newSession as any);
        current = newSession as any;
      }
      
      if (onSessionUpdate && current) {
        onSessionUpdate(current.id, isNew ? text.slice(0, 60) : undefined);
      }
      const assistantTurn: Turn = {
        kind: "assistant",
        id: nextId("assistant"),
        response,
        at: Date.now(),
      };
      setTurns((previous) => [...previous, assistantTurn]);
    } catch (failure) {
      setError(classify(failure));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }, []);

  const send = useCallback(
    (raw: string) => {
      const text = raw.trim();
      if (!text || busyRef.current) {
        return;
      }
      const userTurn: Turn = { kind: "user", id: nextId("user"), text, at: Date.now() };
      setTurns((previous) => [...previous, userTurn]);
      void runSend(text);
    },
    [runSend],
  );

  const retry = useCallback(() => {
    if (busyRef.current) {
      return;
    }
    // The failed user message stays visible; re-run the same attempt.
    void runSend(lastAttemptRef.current);
  }, [runSend]);

  const reset = useCallback(() => {
    if (busyRef.current) {
      return;
    }
    sessionRef.current = null;
    setSession(null);
    setTurns([]);
    setError(null);
  }, []);

  const loadSession = useCallback(async (session_id: string) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setBusy(true);
    setError(null);
    try {
      const history = await getSessionHistory(session_id);
      sessionRef.current = history.session;
      setSession(history.session);
      
      const nextLanguage = history.session.preferred_language;
      languageRef.current = nextLanguage;
      setLanguageState(nextLanguage);
      
      const nextTurns: Turn[] = [];
      const userMessages = history.messages.filter(m => m.role === "user");
      
      for (let i = 0; i < userMessages.length; i++) {
         const msg = userMessages[i];
         nextTurns.push({ kind: "user", id: msg.id, text: msg.text, at: Date.parse(msg.created_at) });
         const resp = history.responses[i];
         if (resp) {
            nextTurns.push({ kind: "assistant", id: nextId("assistant"), response: resp, at: Date.parse(resp.clinician_summary?.generated_at || msg.created_at) });
         }
      }
      setTurns(nextTurns);
    } catch (failure) {
      setError(classify(failure));
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }, []);

  const setLanguage = useCallback((next: Language) => {
    if (busyRef.current || next === languageRef.current) {
      return;
    }
    // The backend session binds a preferred language, so a language switch
    // starts a fresh conversation rather than silently mixing languages.
    sessionRef.current = null;
    setSession(null);
    setTurns([]);
    setError(null);
    setLanguageState(next);
  }, []);

  const started = turns.length > 0 || busy;

  return {
    language,
    session,
    turns,
    busy,
    error,
    started,
    send,
    retry,
    reset,
    setLanguage,
    loadSession,
  };
}
