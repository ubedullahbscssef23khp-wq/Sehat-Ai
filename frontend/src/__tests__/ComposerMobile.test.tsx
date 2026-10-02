import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { Composer } from "../components/Composer";

describe("Composer - Mobile Rendering Constraints", () => {
  beforeEach(() => {
    (window as any).SpeechRecognition = vi.fn();
  });
  
  afterEach(() => {
    delete (window as any).SpeechRecognition;
  });

  it("renders composer field layout without breaking horizontal overflow rules implicitly", () => {
    const { container } = render(
      <Composer
        language="en"
        value="A very long message string that simulates what happens when a user types a lot of text into the composer on a narrow mobile device."
        disabled={false}
        onChange={vi.fn()}
        onSubmit={vi.fn()}
      />
    );
    
    // We mainly verify the structural elements exist alongside each other
    // and that the voice input enhancement doesn't alter the primary flex architecture
    const textarea = screen.getByRole("textbox");
    const sendButton = screen.getByRole("button", { name: "Send" });
    const actionsContainer = container.querySelector(".composer__actions");
    
    expect(textarea).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
    expect(actionsContainer).toBeInTheDocument();
  });
});
