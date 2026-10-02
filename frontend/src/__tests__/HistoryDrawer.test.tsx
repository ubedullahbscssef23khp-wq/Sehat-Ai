import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { HistoryDrawer } from "../components/HistoryDrawer";

vi.mock("../state/useHistory", () => ({
  useHistory: () => ({
    history: [{ id: "123", preview: "Test preview", createdAt: 1000, updatedAt: 1000 }],
    remove: vi.fn(),
  }),
}));

describe("HistoryDrawer", () => {
  it("renders and opens the drawer", () => {
    render(<HistoryDrawer language="en" onSelect={vi.fn()} />);
    
    // Open drawer
    const openButton = screen.getByRole("button", { name: "History" });
    fireEvent.click(openButton);
    
    // Assert content
    expect(screen.getByText("History")).toBeInTheDocument();
    expect(screen.getByText("Test preview")).toBeInTheDocument();
  });
});
