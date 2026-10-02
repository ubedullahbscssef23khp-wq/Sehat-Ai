import re

with open('frontend/src/components/ClinicianSummaryView.tsx', 'r') as f:
    c = f.read()

c = c.replace('summary.triage_decision.rationale', 'summary.triage_decision.next_actions.map((n) => n.en).join(", ")')

with open('frontend/src/components/ClinicianSummaryView.tsx', 'w') as f:
    f.write(c)

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'r') as f:
    c = f.read()

c = c.replace('import { strings } from "../i18n/strings";\n', '')

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'w') as f:
    f.write(c)
