import sys
path = 'frontend/src/__tests__/App.test.tsx'
content = open(path).read()

new_content = content.replace(
'''describe("App UI State & Integration", () => {''',
'''describe("App UI State & Integration", () => {
  it("starts a new session when language is switched", async () => {
    const user = userEvent.setup();
    const mockSession1 = {
      id: "session-en",
      created_at: "2026-09-04T00:00:00Z",
      preferred_language: "en" as const,
      status: "collecting" as const,
    };
    const mockSession2 = {
      id: "session-ur",
      created_at: "2026-09-04T00:00:00Z",
      preferred_language: "ur" as const,
      status: "collecting" as const,
    };
    const mockResponse = syntheticGuidanceResponse("routine");

    vi.mocked(client.createSession).mockResolvedValueOnce(mockSession1);
    vi.mocked(client.sendMessage).mockResolvedValueOnce(mockResponse);

    render(<App />);
    const input = screen.getByPlaceholderText(/Describe your symptoms/i);
    const sendButton = screen.getByRole("button", { name: /Send/i });

    // Send first message
    await user.type(input, "Headache");
    await user.click(sendButton);
    expect(client.createSession).toHaveBeenCalledWith("en");
    expect(client.sendMessage).toHaveBeenCalledWith("session-en", "Headache");

    // Wait for response
    expect(await screen.findByText("Routine Care")).toBeInTheDocument();

    // Switch language
    const langPicker = screen.getByLabelText(/English/i);
    await user.selectOptions(langPicker, "ur");

    // UI should reset to landing state
    expect(screen.queryByText("Routine Care")).not.toBeInTheDocument();

    // Send second message
    vi.mocked(client.createSession).mockResolvedValueOnce(mockSession2);
    vi.mocked(client.sendMessage).mockResolvedValueOnce(mockResponse);
    
    // In Urdu, the placeholder is different, but for testing we can just find it by role or get newly rendered one
    const inputUr = screen.getByRole("textbox");
    await user.type(inputUr, "درد");
    const sendButtonUr = screen.getByRole("button", { name: /Send|بھیجیں/i });
    await user.click(sendButtonUr);

    expect(client.createSession).toHaveBeenCalledWith("ur");
    expect(client.sendMessage).toHaveBeenCalledWith("session-ur", "درد");
  });
'''
)

open(path, 'w').write(new_content)
