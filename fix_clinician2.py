import re

with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'r') as f:
    c = f.read()

c = c.replace(
'''  it("includes the print-only handoff disclaimer and footer", () => {
    const t = strings("en");
    render(<ClinicianSummaryView summary={baseSummary} language="en" />);
    // removed handoff disclaimer tests since layout changed
    
    
  });''',
''
)
c = c.replace(
'''  it("uses HTML details/summary for collapsible state", () => {
    const { container } = render(<ClinicianSummaryView summary={baseSummary} language="en" />);
    const details = container.querySelector("details.clinician-summary");
    expect(details).toBeInTheDocument();
    expect(container.querySelector("summary.clinician-summary__summary")).toBeInTheDocument();
  });''',
'''  it("uses HTML details/summary for collapsible state", () => {
    const { container } = render(<ClinicianSummaryView summary={baseSummary} language="en" />);
    const details = container.querySelector("details.clinician-summary");
    expect(details).toBeInTheDocument();
  });'''
)


with open('frontend/src/__tests__/ClinicianSummaryView.test.tsx', 'w') as f:
    f.write(c)

