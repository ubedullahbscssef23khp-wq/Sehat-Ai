import { renderHook, act } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { useVoiceInput } from "../hooks/useVoiceInput";

describe("useVoiceInput", () => {
  let MockSpeechRecognition: any;
  let mockRecognitionInstance: any;

  beforeEach(() => {
    mockRecognitionInstance = {
      start: vi.fn(),
      stop: vi.fn(),
      continuous: false,
      interimResults: false,
      lang: "",
      onstart: null,
      onresult: null,
      onerror: null,
      onend: null,
    };
    
    MockSpeechRecognition = vi.fn(() => mockRecognitionInstance);
    (window as any).SpeechRecognition = MockSpeechRecognition;
  });

  afterEach(() => {
    delete (window as any).SpeechRecognition;
    vi.restoreAllMocks();
  });

  it("initializes as idle when supported", () => {
    const { result } = renderHook(() => useVoiceInput({ language: "en" }));
    expect(result.current.state).toBe("idle");
    expect(result.current.transcript).toBe("");
  });

  it("initializes as unsupported when SpeechRecognition is missing", () => {
    delete (window as any).SpeechRecognition;
    const { result } = renderHook(() => useVoiceInput({ language: "en" }));
    expect(result.current.state).toBe("unsupported");
  });

  it("starts listening and updates transcript on result", () => {
    const { result } = renderHook(() => useVoiceInput({ language: "en" }));
    
    act(() => {
      result.current.start();
    });

    expect(mockRecognitionInstance.start).toHaveBeenCalled();
    
    act(() => {
      if (mockRecognitionInstance.onstart) mockRecognitionInstance.onstart();
    });
    
    expect(result.current.state).toBe("listening");

    act(() => {
      if (mockRecognitionInstance.onresult) {
        mockRecognitionInstance.onresult({
          resultIndex: 0,
          results: [[{ transcript: "hello world" }]]
        });
      }
    });

    expect(result.current.transcript).toBe("hello world");
  });

  it("stops listening when stop is called", () => {
    const { result } = renderHook(() => useVoiceInput({ language: "en" }));
    
    act(() => {
      result.current.start();
    });
    
    act(() => {
      if (mockRecognitionInstance.onstart) mockRecognitionInstance.onstart();
    });
    
    expect(result.current.state).toBe("listening");
    
    act(() => {
      result.current.stop();
    });

    expect(mockRecognitionInstance.stop).toHaveBeenCalled();
    expect(result.current.state).toBe("idle");
  });
  
  it("sets correct language code for Urdu", () => {
    const { result } = renderHook(() => useVoiceInput({ language: "ur" }));
    act(() => {
      result.current.start();
    });
    expect(mockRecognitionInstance.lang).toBe("ur-PK");
  });
});
