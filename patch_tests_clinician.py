import re

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    'expect(screen.getByRole("heading", { level: 3, name: "Clinician Summary" })).toBeInTheDocument();',
    'expect(screen.getByRole("heading", { level: 2, name: "Clinician Summary" })).toBeInTheDocument();'
)

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'w') as f:
    f.write(c)

with open('frontend/src/__tests__/AssistantMessage.test.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    'expect(screen.getByRole("heading", { level: 3, name: strings("en").clinicianSummaryLabel })).toBeInTheDocument();',
    'expect(screen.getByRole("heading", { level: 2, name: strings("en").clinicianSummaryLabel })).toBeInTheDocument();'
)

with open('frontend/src/__tests__/AssistantMessage.test.tsx', 'w') as f:
    f.write(c)

