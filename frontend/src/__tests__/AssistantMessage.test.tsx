import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AssistantMessage } from "../components/AssistantMessage";
import { strings } from "../i18n/strings";
import { syntheticGuidanceResponse, syntheticLocalized } from "./fixtures";

describe("AssistantMessage", () => {
  it("renders normal guidance user message and triage card", () => {
    const response = syntheticGuidanceResponse("routine", {
      user_message: syntheticLocalized("Synthetic guidance text for patient"),
    });

    render(<AssistantMessage response={response} language="en" />);

    expect(screen.getByText("Synthetic guidance text for patient")).toBeInTheDocument();
    expect(screen.getByRole("heading", { level: 3, name: strings("en").triageLabels.routine })).toBeInTheDocument();
  });

  it("renders disclaimer block when supplied", () => {
    const response = syntheticGuidanceResponse("routine", {
      disclaimers: [syntheticLocalized("Synthetic non-removable disclaimer line")],
    });

    render(<AssistantMessage response={response} language="en" />);

    expect(screen.getByText("Synthetic non-removable disclaimer line")).toBeInTheDocument();
  });

  it("renders clinician summary when supplied", () => {
    const response = syntheticGuidanceResponse("routine");
    render(<AssistantMessage response={response} language="en" />);

    expect(screen.getAllByRole("heading").length).toBeGreaterThan(0);
  });

  it("omits clinician summary when clinician_summary is null", () => {
    const response = syntheticGuidanceResponse("routine", {
      clinician_summary: null,
    });
    render(<AssistantMessage response={response} language="en" />);

    expect(screen.queryByText(strings("en").clinicianSummaryHeading)).toBeNull();
  });

  it("renders evidence when supplied", () => {
    const response = syntheticGuidanceResponse("routine", {
      evidence: [
        {
          source: "Synthetic Clinical Source",
          date_reviewed: "2026-01-01",
          snippet: "Synthetic medical snippet",
        },
      ],
    });
    render(<AssistantMessage response={response} language="en" />);

    expect(screen.getByText("Synthetic Clinical Source")).toBeInTheDocument();
    expect(screen.getByText("Synthetic medical snippet")).toBeInTheDocument();
  });

  it("renders follow-up questions when supplied", () => {
    const response = syntheticGuidanceResponse("routine", {
      follow_up_questions: [syntheticLocalized("Synthetic follow-up question")],
    });
    render(<AssistantMessage response={response} language="en" />);

    expect(screen.getByText("Synthetic follow-up question")).toBeInTheDocument();
  });

  it("resolves localized content accurately for Urdu", () => {
    const response = syntheticGuidanceResponse("routine", {
      user_message: syntheticLocalized("English user message"),
    });
    render(<AssistantMessage response={response} language="ur" />);

    expect(screen.getByText("English user message ur")).toBeInTheDocument();
    expect(screen.queryByText("English user message")).toBeNull();
  });
});
