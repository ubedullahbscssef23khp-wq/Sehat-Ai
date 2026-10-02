import type { ClinicianSummary, GuidanceResponse, TriageDecision, LocalizedText, TriageLevel } from "../api/types";

export const syntheticLocalized = (text: string): LocalizedText => ({
  en: text,
  ur: text + " ur",
  sd: text + " sd",
});

export const syntheticTriageDecision = (level: TriageLevel = "routine", overrides: Partial<TriageDecision> = {}): TriageDecision => ({
  level,
  fired_rule_ids: [],
  next_actions: [syntheticLocalized("Action")],
  self_care_limits: [],
  recheck_advice: null,
  limited_confidence: false,
  ...overrides
});

export const syntheticGuidanceResponse = (level: TriageLevel = "routine", overrides: Partial<GuidanceResponse> = {}): GuidanceResponse => ({
  session_id: "test",
  user_message: syntheticLocalized("Synthetic guidance text for patient"),
  triage: syntheticTriageDecision(level),
  follow_up_questions: [syntheticLocalized("Follow up question")],
  evidence: [],
  evidence_note: null,
  disclaimers: [],
  clinician_summary: null,
  ...overrides
});

export const syntheticClinicianSummary = (): ClinicianSummary => ({
  structured_case: {
    chief_complaint: "Test",
    symptoms: [],
    demographics: {
      age_group: null,
      pregnant: null
    },
    red_flag_signals: [],
    associated_factors: [],
    missing_fields: [],
    confidence: 2,
    raw_excerpt: ""
  },
  fired_rules: [],
  timeline: [],
  triage_decision: syntheticTriageDecision(),
  generated_at: new Date().toISOString(),
  model_attribution: null,
});
