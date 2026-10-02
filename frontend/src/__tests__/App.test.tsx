import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "../App";
import * as client from "../api/client";
import * as health from "../api/health";
import { strings } from "../i18n/strings";
import { syntheticGuidanceResponse, syntheticLocalized } from "./fixtures";

vi.mock("../api/health");
vi.mock("../api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../api/client")>();
  return { 
    ...actual, 
    v1GetHistorySessions: vi.fn().mockResolvedValue([]), 
    v1GetClinicalSummary: vi.fn().mockResolvedValue(null), 
    v1SendMessage: vi.fn() 
  };
});

describe("App UI State & Integration", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(health.fetchHealth).mockResolvedValue({
      status: "ok",
      service: "sehat-ai",
      env: "test",
      llm_provider: "mock",
    });
  });

  it("starts a new session when language is switched", async () => {
    const user = userEvent.setup();
    const mockResponse1 = syntheticGuidanceResponse("routine");
    mockResponse1.session_id = "session-en";
    
    const mockResponse2 = syntheticGuidanceResponse("routine");
    mockResponse2.session_id = "session-ur";

    vi.mocked(client.v1SendMessage as any).mockResolvedValueOnce(mockResponse1);
    
    render(<App />);
    const input = screen.getByPlaceholderText(/Describe your symptoms/i);
    const sendButton = screen.getByRole("button", { name: /Send/i });
    
    // Send first message
    await user.type(input, "Headache");
    await user.click(sendButton);
    
    expect(client.v1SendMessage).toHaveBeenCalledWith("Headache", undefined, "en");

    // Wait for response
    expect(await screen.findByRole("heading", { name: /Routine Care/i })).toBeInTheDocument();

    // Switch language
    const langPicker = screen.getByRole("button", { name: "UR" });
    await user.click(langPicker);

    // UI should reset to landing state
    expect(screen.queryByRole("heading", { name: /Routine Care/i })).not.toBeInTheDocument();

    // Send second message
    vi.mocked(client.v1SendMessage as any).mockResolvedValueOnce(mockResponse2);
    
    const inputUr = screen.getByRole("textbox");
    await user.type(inputUr, "درد");
    const sendButtonUr = screen.getByRole("button", { name: /Send|بھیجیں/i });
    await user.click(sendButtonUr);
    
    expect(client.v1SendMessage).toHaveBeenCalledWith("درد", undefined, "ur");
  });

  it("renders initial landing state with Hero and empty-state composer", async () => {
    const t = strings("en");
    render(<App />);
    expect(screen.getAllByText(t.appName).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByRole("heading", { level: 2 })[0]).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: t.inputPlaceholder })).toBeInTheDocument();
  });

  it("renders assistant response after sending a message", async () => {
    const user = userEvent.setup();
    const mockResponse = syntheticGuidanceResponse("routine", {
      user_message: syntheticLocalized("Synthetic clinical advice for user"),
    });
    mockResponse.session_id = "test-session-1";
    
    vi.mocked(client.v1SendMessage as any).mockResolvedValueOnce(mockResponse);
    render(<App />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Synthetic symptom report{Enter}");

    // Shows user message in chat
    expect(screen.getByText("Synthetic symptom report")).toBeInTheDocument();

    // Awaits assistant message response
    await waitFor(() => {
      expect(screen.getByText("Synthetic clinical advice for user")).toBeInTheDocument();
    });

    // Shows New Conversation button now that conversation is active
    expect(screen.getAllByRole("button", { name: strings("en").newConversation })[0]).toBeInTheDocument();
  });

  it("renders error banner when API sendMessage fails", async () => {
    const user = userEvent.setup();
    
    vi.mocked(client.v1SendMessage as any).mockRejectedValueOnce(
      new client.ApiError(503, "llm_unavailable", "Service unavailable")
    );
    render(<App />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Fever symptom{Enter}");

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(strings("en").errorUnavailable)).toBeInTheDocument();
    });
  });

  it("resets conversation to landing state when New Conversation is clicked", async () => {
    const user = userEvent.setup();
    const mockResponse = syntheticGuidanceResponse("routine", {
      user_message: syntheticLocalized("Synthetic advice"),
    });
    mockResponse.session_id = "test-session-reset";
    
    vi.mocked(client.v1SendMessage as any).mockResolvedValueOnce(mockResponse);
    render(<App />);

    const input = screen.getByRole("textbox");
    await user.type(input, "Initial message{Enter}");

    await waitFor(() => {
      expect(screen.getByText("Synthetic advice")).toBeInTheDocument();
    });

    const newConversationBtn = screen.getAllByRole("button", {
      name: strings("en").newConversation,
    })[0];
    await user.click(newConversationBtn);

    // Returns to Hero state
    expect(screen.getAllByRole("heading", { level: 2 })[0]).toBeInTheDocument();
    expect(screen.queryByText("Synthetic advice")).toBeNull();
  });

  it("renders server error banner on HTTP 502 Bad Gateway and maintains AppShell", async () => {
    const user = userEvent.setup();
    vi.mocked(client.v1SendMessage as any).mockRejectedValueOnce(
      new client.ApiError(502, "bad_gateway", "Bad Gateway")
    );

    render(<App />);
    const input = screen.getByRole("textbox");
    await user.type(input, "Acute pain{Enter}");

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(strings("en").errorServer)).toBeInTheDocument();
    });
    expect(screen.getByText(strings("en").appName)).toBeInTheDocument();
  });

  it("renders server error banner on HTTP 504 Gateway Timeout", async () => {
    const user = userEvent.setup();
    vi.mocked(client.v1SendMessage as any).mockRejectedValueOnce(
      new client.ApiError(504, "gateway_timeout", "Gateway Timeout")
    );

    render(<App />);
    const input = screen.getByRole("textbox");
    await user.type(input, "Persistent cough{Enter}");

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(strings("en").errorServer)).toBeInTheDocument();
    });
  });

  it("renders offline error banner on network failure with retry button", async () => {
    const user = userEvent.setup();
    vi.mocked(client.v1SendMessage as any).mockRejectedValueOnce(
      new client.NetworkError()
    );

    render(<App />);
    const input = screen.getByRole("textbox");
    await user.type(input, "Severe headache{Enter}");

    await waitFor(() => {
      expect(screen.getByRole("alert")).toBeInTheDocument();
      expect(screen.getByText(strings("en").errorOffline)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: strings("en").retry })).toBeInTheDocument();
    });
  });
});
