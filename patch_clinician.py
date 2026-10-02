with open('frontend/src/components/ClinicianSummaryView.tsx', 'r') as f:
    c = f.read()

c = c.replace(
    '{summary.structured_case.symptoms.length > 0',
    '{summary.structured_case.symptoms && summary.structured_case.symptoms.length > 0'
)

with open('frontend/src/components/ClinicianSummaryView.tsx', 'w') as f:
    f.write(c)
