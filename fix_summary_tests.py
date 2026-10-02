import re

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'r') as f:
    c = f.read()

c = c.replace('const baseSummary = {} as any;', 'const baseSummary = { structured_case: { chief_complaint: "test", symptoms: [], demographics: { age_group: null, pregnant: null }, red_flag_signals: [] }, fired_rules: [], timeline: [], triage_decision: { next_actions: [] } } as any;')

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'w') as f:
    f.write(c)

