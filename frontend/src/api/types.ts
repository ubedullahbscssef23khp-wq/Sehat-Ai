/** Backend contract types — mirror the pydantic models exactly
 * (backend/app/models/domain.py). The backend is the source of truth;
 * nothing here is invented or computed on the client. */

export type Language = "en" | "ur" | "sd";

export type TriageLevel =
  | "emergency"
  | "urgent_same_day"
  | "routine"
  | "self_care"
  | "needs_more_info";

export type SessionStatus =
  | "collecting"
  | "assessing"
  | "guided"
  | "escalated"
  | "closed";

export interface LocalizedText {
  en: string;
  ur: string | null;
  sd: string | null;
}

export interface Session {
  id: string;
  created_at: string;
  preferred_language: Language;
  status: SessionStatus;
}

export interface Citation {
  source: string;
  date_reviewed: string;
  snippet: string;
}

export interface TriageDecision {
  level: TriageLevel;
  fired_rule_ids: string[];
  next_actions: LocalizedText[];
  self_care_limits: LocalizedText[];
  recheck_advice: LocalizedText | null;
  limited_confidence: boolean;
}

export interface GuidanceResponse {
  session_id: string;
  user_message: LocalizedText;
  triage: TriageDecision;
  follow_up_questions: LocalizedText[];
  evidence: Citation[];
  evidence_note: LocalizedText | null;
  disclaimers: LocalizedText[];
}

export interface ErrorEnvelope {
  error: {
    code: string;
    message: string;
    locations?: unknown;
  };
}

/** Same selection rule as LocalizedText.for_language on the backend. */
export function localized(text: LocalizedText, language: Language): string {
  if (language === "ur" && text.ur !== null) return text.ur;
  if (language === "sd" && text.sd !== null) return text.sd;
  return text.en;
}
