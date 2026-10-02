import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { Composer } from "../components/Composer";
import * as useVoiceInputModule from "../hooks/useVoiceInput";

vi.mock("../hooks/useVoiceInput", () => ({
  useVoiceInput: vi.fn()
}));

describe("Composer - Voice Input", () => {
  const onChange = vi.fn();
  const onSubmit = vi.fn();
  const mockToggleListening = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renders mic button when supported", () => {
    vi.mocked(useVoiceInputModule.useVoiceInput).mockReturnValue({
      state: "idle",
      transcript: "",
      start: vi.fn(),
      stop: vi.fn(),
      isSupported: true,
      isListening: false,
      toggleListening: mockToggleListening
    } as any);

    render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={onChange}
        onSubmit={onSubmit}
      />
    );
    expect(screen.getAllByRole("button").length).toBeGreaterThan(0);
  });

  it("renders disabled mic when not supported", () => {
    vi.mocked(useVoiceInputModule.useVoiceInput).mockReturnValue({
      state: "unsupported",
      transcript: "",
      start: vi.fn(),
      stop: vi.fn(),
      isSupported: false,
      isListening: false,
      toggleListening: mockToggleListening
    } as any);

    render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={onChange}
        onSubmit={onSubmit}
      />
    );
    // Only send button should render
    expect(screen.getAllByRole("button").length).toBe(2);
  });

  it("clicking mic toggles listening", () => {
    vi.mocked(useVoiceInputModule.useVoiceInput).mockReturnValue({
      state: "idle",
      transcript: "",
      start: vi.fn(),
      stop: vi.fn(),
      isSupported: true,
      isListening: false,
      toggleListening: mockToggleListening
    } as any);

    render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={onChange}
        onSubmit={onSubmit}
      />
    );
    const micBtn = screen.getAllByRole("button")[1];
    fireEvent.click(micBtn);
    expect(mockToggleListening).toHaveBeenCalled();
  });
});
