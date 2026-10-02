import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { ErrorBanner } from "../components/ErrorBanner";
import { strings } from "../i18n/strings";
import type { UiError } from "../state/useChat";

describe("ErrorBanner", () => {
  it("renders offline error message with retry button", () => {
    const error: UiError = { kind: "offline" };
    const t = strings("en");
    const onRetry = vi.fn();

    render(
      <ErrorBanner
        error={error}
        language="en"
        onRetry={onRetry}
        onNewConversation={vi.fn()}
      />
    );

    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText(t.errorOffline)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: t.retry })).toBeInTheDocument();
  });

  it("invokes onRetry when retry button is clicked", async () => {
    const user = userEvent.setup();
    const error: UiError = { kind: "server" };
    const onRetry = vi.fn();

    render(
      <ErrorBanner
        error={error}
        language="en"
        onRetry={onRetry}
        onNewConversation={vi.fn()}
      />
    );

    const retryButton = screen.getByRole("button", { name: strings("en").retry });
    await user.click(retryButton);

    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("renders new conversation button for restartable errors (closed session)", async () => {
    const user = userEvent.setup();
    const error: UiError = { kind: "closed" };
    const t = strings("en");
    const onNewConversation = vi.fn();

    render(
      <ErrorBanner
        error={error}
        language="en"
        onRetry={vi.fn()}
        onNewConversation={onNewConversation}
      />
    );

    expect(screen.getByText(t.errorClosed)).toBeInTheDocument();
    const newConvBtn = screen.getByRole("button", { name: t.newConversation });
    expect(newConvBtn).toBeInTheDocument();

    await user.click(newConvBtn);
    expect(onNewConversation).toHaveBeenCalledOnce();
  });

  it("renders localized error text in Urdu", () => {
    const error: UiError = { kind: "unavailable" };
    const tUr = strings("ur");

    render(
      <ErrorBanner
        error={error}
        language="ur"
        onRetry={vi.fn()}
        onNewConversation={vi.fn()}
      />
    );

    expect(screen.getByText(tUr.errorUnavailable)).toBeInTheDocument();
  });
});
