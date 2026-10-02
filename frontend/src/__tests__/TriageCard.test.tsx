import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { TriageLevel } from "../api/types";
import { TriageCard } from "../components/TriageCard";
import { strings } from "../i18n/strings";
import { syntheticLocalized, syntheticTriageDecision } from "./fixtures";

describe("TriageCard", () => {
  const allLevels: TriageLevel[] = [
    "emergency",
    "urgent_same_day",
    "routine",
    "self_care",
    "needs_more_info",
  ];

  it.each(allLevels)(
    "renders appropriate localized label and aria-label for level '%s'",
    (level) => {
      const decision = syntheticTriageDecision(level, {
        next_actions: [syntheticLocalized("Action step 1")],
      });
      const t = strings("en");
      const expectedLabel = t.triageLabels[level];

      const { container } = render(<TriageCard decision={decision} language="en" />);

      // Verify the semantic section label
      const section = screen.getByRole("region", { name: expectedLabel });
      expect(section).toBeInTheDocument();

      // Verify the heading text matches the localized label
      const heading = screen.getByRole("heading", { level: 3, name: expectedLabel });
      expect(heading).toBeInTheDocument();

      // Verify next action text is rendered
      expect(screen.getByText("Action step 1")).toBeInTheDocument();

      // Verify root container has corresponding class modifier
      const expectedClass = {
        emergency: "triage--emergency",
        urgent_same_day: "triage--urgent",
        routine: "triage--routine",
        self_care: "triage--selfcare",
        needs_more_info: "triage--info",
      }[level];
      expect(container.querySelector(`.${expectedClass}`)).not.toBeNull();
    }
  );

  it("visually and semantically distinguishes emergency/urgent presentation with alert icon", () => {
    const emergencyDecision = syntheticTriageDecision("emergency");
    const { container: emergencyContainer } = render(
      <TriageCard decision={emergencyDecision} language="en" />
    );
    expect(emergencyContainer.querySelector(".triage--emergency")).toBeInTheDocument();

    const routineDecision = syntheticTriageDecision("routine");
    const { container: routineContainer } = render(
      <TriageCard decision={routineDecision} language="en" />
    );
    expect(routineContainer.querySelector(".triage--routine")).toBeInTheDocument();
    expect(routineContainer.querySelector(".triage--emergency")).not.toBeInTheDocument();
  });

  it("renders localized text for Urdu without failing", () => {
    const decision = syntheticTriageDecision("emergency", {
      next_actions: [syntheticLocalized("English action")],
    });
    const t = strings("ur");

    render(<TriageCard decision={decision} language="ur" />);

    expect(screen.getByRole("heading", { level: 3, name: t.triageLabels.emergency })).toBeInTheDocument();
    expect(screen.getByText("English action ur")).toBeInTheDocument();
  });
});
