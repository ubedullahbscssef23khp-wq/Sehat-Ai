import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DisclaimerBlock } from "../components/DisclaimerBlock";
import { strings } from "../i18n/strings";
import { syntheticLocalized } from "./fixtures";

describe("DisclaimerBlock", () => {
  it("renders when disclaimers are provided", () => {
    const disclaimers = [
      syntheticLocalized("Synthetic disclaimer line one"),
      syntheticLocalized("Synthetic disclaimer line two"),
    ];
    const t = strings("en");

    render(<DisclaimerBlock disclaimers={disclaimers} language="en" />);

    // Section exists with aria-label
    expect(screen.getByRole("region", { name: t.disclaimerHeading })).toBeInTheDocument();

    // Every supplied disclaimer is rendered
    expect(screen.getByText("Synthetic disclaimer line one")).toBeInTheDocument();
    expect(screen.getByText("Synthetic disclaimer line two")).toBeInTheDocument();
  });

  it("renders multiple disclaimers without omitting any", () => {
    const disclaimers = [
      syntheticLocalized("First statement"),
      syntheticLocalized("Second statement"),
      syntheticLocalized("Third statement"),
    ];

    render(<DisclaimerBlock disclaimers={disclaimers} language="en" />);

    expect(screen.getByText("First statement")).toBeInTheDocument();
    expect(screen.getByText("Second statement")).toBeInTheDocument();
    expect(screen.getByText("Third statement")).toBeInTheDocument();
  });

  it("returns null when disclaimers array is empty (existing behavior)", () => {
    const { container } = render(<DisclaimerBlock disclaimers={[]} language="en" />);
    expect(container.firstChild).toBeNull();
  });

  it("renders localized disclaimer text in Urdu", () => {
    const disclaimers = [
      syntheticLocalized("English disclaimer"),
    ];

    render(<DisclaimerBlock disclaimers={disclaimers} language="ur" />);

    expect(screen.getByText("English disclaimer ur")).toBeInTheDocument();
  });
});
