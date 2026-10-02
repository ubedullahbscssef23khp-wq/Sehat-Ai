import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ClinicianSummaryView } from "../components/ClinicianSummaryView";


describe("ClinicianSummaryView", () => {
  const baseSummary = { structured_case: { chief_complaint: "test", symptoms: [], demographics: { age_group: null, pregnant: null }, red_flag_signals: [] }, fired_rules: [], timeline: [], triage_decision: { next_actions: [] } } as any;
  

  it("renders without crashing", () => {
    const { container } = render(<ClinicianSummaryView summary={baseSummary} language="en" />);
    expect(container).not.toBeNull();
  });
  
  it("renders with urdu", () => {
    const { container } = render(<ClinicianSummaryView summary={baseSummary} language="ur" />);
    expect(container).not.toBeNull();
  });
  
  it("renders with sindhi", () => {
    const { container } = render(<ClinicianSummaryView summary={baseSummary} language="sd" />);
    expect(container).not.toBeNull();
  });
});
