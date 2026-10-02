import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { Composer } from "../components/Composer";
import { strings } from "../i18n/strings";

describe("Composer", () => {
  beforeEach(() => {
    (window as any).SpeechRecognition = vi.fn();
  });
  afterEach(() => {
    delete (window as any).SpeechRecognition;
  });

  it("renders textarea input and submit button", () => {
    const t = strings("en");
    render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={vi.fn()}
        onSubmit={vi.fn()}
      />
    );

    const input = screen.getByRole("textbox", { name: t.inputPlaceholder });
    const sendButton = screen.getByRole("button", { name: t.send });

    expect(input).toBeInTheDocument();
    expect(sendButton).toBeInTheDocument();
  });

  it("calls onChange when user types", async () => {
    const user = userEvent.setup();
    const handleChange = vi.fn();

    render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={handleChange}
        onSubmit={vi.fn()}
      />
    );

    const input = screen.getByRole("textbox");
    await user.type(input, "a");

    expect(handleChange).toHaveBeenCalledWith("a");
  });

  it("submits entered text when submit button is clicked", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(
      <Composer
        language="en"
        value="Synthetic symptom description"
        disabled={false}
        onChange={vi.fn()}
        onSubmit={handleSubmit}
      />
    );

    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(sendButton).not.toBeDisabled();

    await user.click(sendButton);
    expect(handleSubmit).toHaveBeenCalledWith("Synthetic symptom description");
  });

  it("disables submit button and prevents submission when input is empty or whitespace", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    const { rerender } = render(
      <Composer
        language="en"
        value=""
        disabled={false}
        onChange={vi.fn()}
        onSubmit={handleSubmit}
      />
    );

    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(sendButton).toBeDisabled();

    rerender(
      <Composer
        language="en"
        value="   "
        disabled={false}
        onChange={vi.fn()}
        onSubmit={handleSubmit}
      />
    );
    expect(sendButton).toBeDisabled();

    const input = screen.getByRole("textbox");
    await user.type(input, "{Enter}");
    expect(handleSubmit).not.toHaveBeenCalled();
  });

  it("disables input and send button when disabled prop is true (loading/busy state)", () => {
    render(
      <Composer
        language="en"
        value="Synthetic input"
        disabled={true}
        onChange={vi.fn()}
        onSubmit={vi.fn()}
      />
    );

    expect(screen.getByRole("textbox")).toBeDisabled();
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("submits on Enter key press without Shift key", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(
      <Composer
        language="en"
        value="Synthetic user input"
        disabled={false}
        onChange={vi.fn()}
        onSubmit={handleSubmit}
      />
    );

    const input = screen.getByRole("textbox");
    await user.type(input, "{Enter}");

    expect(handleSubmit).toHaveBeenCalledWith("Synthetic user input");
  });

  it("does not submit on Shift+Enter key press", async () => {
    const user = userEvent.setup();
    const handleSubmit = vi.fn();

    render(
      <Composer
        language="en"
        value="Synthetic user input"
        disabled={false}
        onChange={vi.fn()}
        onSubmit={handleSubmit}
      />
    );

    const input = screen.getByRole("textbox");
    await user.click(input);
    await user.keyboard("{Shift>}{Enter}{/Shift}");

    expect(handleSubmit).not.toHaveBeenCalled();
  });
});
