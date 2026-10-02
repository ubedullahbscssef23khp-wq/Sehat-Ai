import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { Citation } from "../api/types";
import { EvidenceList } from "../components/EvidenceList";
import { strings } from "../i18n/strings";
import { syntheticLocalized } from "./fixtures";

describe("EvidenceList", () => {
  const sampleCitations: Citation[] = [
    {
      source: "WHO Clinical Practice Guide",
      date_reviewed: "2024-05-15",
      snippet: "Synthetic clinical guideline excerpt on symptoms.",
    },
    {
      source: "NHS Emergency Overview",
      date_reviewed: "2023-11-20",
      snippet: "Synthetic recommendation excerpt.",
    },
  ];

  it("renders evidence entries with source, date, and snippet", () => {
    const t = strings("en");
    render(<EvidenceList evidence={sampleCitations} evidenceNote={null} language="en" />);

    expect(screen.getByRole("region", { name: t.evidenceHeading })).toBeInTheDocument();
    expect(screen.getByText("WHO Clinical Practice Guide")).toBeInTheDocument();
    expect(screen.getByText("Synthetic clinical guideline excerpt on symptoms.")).toBeInTheDocument();
    expect(screen.getByText("NHS Emergency Overview")).toBeInTheDocument();
    expect(screen.getByText("Synthetic recommendation excerpt.")).toBeInTheDocument();
  });

  it("returns null when evidence is empty and no evidenceNote is provided", () => {
    const { container } = render(
      <EvidenceList evidence={[]} evidenceNote={null} language="en" />
    );
    expect(container.firstChild).toBeNull();
  });

  it("renders honest fallback note when evidence is empty but evidenceNote is provided", () => {
    const t = strings("en");
    const note = syntheticLocalized("No specific guideline matched this query.");

    render(<EvidenceList evidence={[]} evidenceNote={note} language="en" />);

    expect(screen.getByRole("region", { name: t.evidenceHeading })).toBeInTheDocument();
    expect(screen.getByText("No specific guideline matched this query.")).toBeInTheDocument();
  });

  it("renders localized evidence note in Urdu", () => {
    const note = syntheticLocalized("No matching guideline");

    render(<EvidenceList evidence={[]} evidenceNote={note} language="ur" />);

    expect(screen.getByText("No matching guideline ur")).toBeInTheDocument();
  });
});
