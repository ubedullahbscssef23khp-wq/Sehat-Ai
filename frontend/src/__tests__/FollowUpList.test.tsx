import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FollowUpList } from "../components/FollowUpList";
import { strings } from "../i18n/strings";
import { syntheticLocalized } from "./fixtures";

describe("FollowUpList", () => {
  it("renders a single follow-up question in paragraph format", () => {
    const questions = [syntheticLocalized("Have your symptoms lasted longer than 48 hours?")];
    const t = strings("en");

    render(<FollowUpList questions={questions} language="en" />);

    expect(screen.getByRole("region", { name: t.followUpHeading })).toBeInTheDocument();
    expect(screen.getByText("Have your symptoms lasted longer than 48 hours?")).toBeInTheDocument();
  });

  it("renders multiple follow-up questions as an ordered list", () => {
    const questions = [
      syntheticLocalized("Question 1"),
      syntheticLocalized("Question 2"),
      syntheticLocalized("Question 3"),
    ];

    render(<FollowUpList questions={questions} language="en" />);

    expect(screen.getByText("Question 1")).toBeInTheDocument();
    expect(screen.getByText("Question 2")).toBeInTheDocument();
    expect(screen.getByText("Question 3")).toBeInTheDocument();
    expect(screen.getByRole("list")).toBeInTheDocument();
  });

  it("returns null when questions list is empty", () => {
    const { container } = render(<FollowUpList questions={[]} language="en" />);
    expect(container.firstChild).toBeNull();
  });

  it("renders localized follow-up question in Urdu", () => {
    const questions = [
      syntheticLocalized("English question"),
    ];

    render(<FollowUpList questions={questions} language="ur" />);

    expect(screen.getByText("English question ur")).toBeInTheDocument();
  });
});
