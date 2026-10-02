import re

with open('frontend/src/__tests__/fixtures.ts', 'r') as f:
    c = f.read()

# Add missing mock text for synthetic localized strings so they don't return undefined.
c = c.replace(
'''export const syntheticGuidanceResponse = (): GuidanceResponse => ({
  session_id: "test",
  triage: syntheticTriageDecision(),
  follow_up_questions: [],
  evidence: [],
  evidence_note: null,
  disclaimers: [],
  clinician_summary: null,
});''',
'''export const syntheticGuidanceResponse = (): GuidanceResponse => ({
  session_id: "test",
  triage: syntheticTriageDecision(),
  follow_up_questions: [syntheticLocalized("Follow up question")],
  evidence: [],
  evidence_note: null,
  disclaimers: [],
  clinician_summary: null,
});'''
)

with open('frontend/src/__tests__/fixtures.ts', 'w') as f:
    f.write(c)

