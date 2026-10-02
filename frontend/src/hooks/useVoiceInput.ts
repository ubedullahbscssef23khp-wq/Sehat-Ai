import { useCallback, useEffect, useRef, useState } from "react";
import type { Language } from "../api/types";

export type VoiceState = "idle" | "listening" | "unsupported" | "error";

interface UseVoiceInputResult {
  state: VoiceState;
  transcript: string;
  start: () => void;
  stop: () => void;
  isListening: boolean;
  isSupported: boolean;
  toggleListening: () => void;
}

const LANGUAGE_CODES: Record<Language, string> = {
  en: "en-US",
  ur: "ur-PK",
  sd: "sd-PK",
};

export function useVoiceInput(params: any): UseVoiceInputResult {
  const language = params?.language || "en";
  const onResult = params?.onResult;
  
  const getSpeechRecognition = useCallback(() => {
    return (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  }, []);

  const [state, setState] = useState<VoiceState>("unsupported");
  const [transcript, setTranscript] = useState("");
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
      if (getSpeechRecognition() && state === "unsupported") {
          setState("idle");
      } else if (!getSpeechRecognition() && state !== "unsupported") {
          setState("unsupported");
      }
  }, [getSpeechRecognition]); 

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const start = useCallback(() => {
    const SpeechRecognition = getSpeechRecognition();
    if (!SpeechRecognition) {
      setState("unsupported");
      return;
    }
    if (state === "listening") {
      return;
    }
    const recognition = new SpeechRecognition();
    recognitionRef.current = recognition;

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = LANGUAGE_CODES[language as Language];

    recognition.onstart = () => {
      setState("listening");
      setTranscript("");
    };

    recognition.onresult = (event: any) => {
      let currentTranscript = "";
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        currentTranscript += event.results[i][0].transcript;
      }
      setTranscript(currentTranscript);
      if (onResult) {
        onResult(currentTranscript);
      }
    };

    recognition.onerror = (event: any) => {
      if (event.error !== 'no-speech') {
        setState("error");
      }
    };

    recognition.onend = () => {
      setState((prev) => (prev === "listening" ? "idle" : prev));
    };

    try {
      recognition.start();
    } catch (e) {
      setState("error");
    }
  }, [language, state, getSpeechRecognition, onResult]);

  const stop = useCallback(() => {
    if (recognitionRef.current && state === "listening") {
      recognitionRef.current.stop();
      setState("idle");
    }
  }, [state]);

  const toggleListening = useCallback(() => {
    if (state === "listening") {
      stop();
    } else {
      start();
    }
  }, [state, start, stop]);

  return { 
    state, 
    transcript, 
    start, 
    stop,
    isListening: state === "listening",
    isSupported: state !== "unsupported",
    toggleListening
  };
}
