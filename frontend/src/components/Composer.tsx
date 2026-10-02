import { forwardRef, useEffect, useRef } from "react";
import type { Language } from "../api/types";
import { strings, directionOf } from "../i18n/strings";
import { SendIcon, MicIcon } from "./Icons";
import { useVoiceInput } from "../hooks/useVoiceInput";

interface ComposerProps {
  language: Language;
  value: string;
  disabled: boolean;
  onChange: (val: string) => void;
  onSubmit: (val: string) => void;
}

export const Composer = forwardRef<HTMLTextAreaElement, ComposerProps>(
  ({ language, value, disabled, onChange, onSubmit }, externalRef) => {
    const t = strings(language) as any;
    const dir = directionOf(language);
    const { isListening, isSupported, toggleListening } = useVoiceInput({
      language,
      onResult: onChange,
      onError: (err: any) => alert(err),
    });

    const localRef = useRef<HTMLTextAreaElement>(null);
    const ref = (externalRef as React.RefObject<HTMLTextAreaElement>) || localRef;

    useEffect(() => {
      if (ref.current) {
        ref.current.style.height = "auto";
        ref.current.style.height = `${Math.min(ref.current.scrollHeight, 120)}px`;
      }
    }, [value, ref]);

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        if (value.trim() && !disabled) {
          onSubmit(value.trim());
        }
      }
    };

    return (
    <div className="pt-2 w-full relative">
      <div 
        role="form" 
        aria-label={t.composerLabel}
        className="p-2 rounded-full bg-[#0f172a]/85 border border-white/[0.12] backdrop-blur-2xl shadow-[0_15px_35px_rgba(0,0,0,0.8)] flex items-center gap-3 transition-all focus-within:border-cyan-500/30 focus-within:bg-[#0f172a]/95 focus-within:shadow-[0_0_20px_rgba(6,182,212,0.15)]"
      >
        <button
          type="button"
          className="h-9 w-9 rounded-full flex items-center justify-center text-slate-400 hover:text-white transition-colors flex-shrink-0"
          disabled={disabled}
          title={t.attach || "Attach file"}
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/></svg>
        </button>
        {isSupported && (
          <button
            type="button"
            className={`h-9 w-9 rounded-full flex items-center justify-center transition-colors flex-shrink-0 ${
              isListening
                ? "bg-rose-500/20 text-rose-400 border border-rose-500/30 animate-pulse shadow-[0_0_15px_rgba(244,63,94,0.3)]"
                : "text-slate-400 hover:text-cyan-400"
            }`}
            onClick={toggleListening}
            disabled={disabled}
            title={isListening ? t.stopVoice : t.startVoice}
          >
            <MicIcon size={18} />
          </button>
        )}
        <textarea
          ref={ref}
          className="flex-1 bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none resize-none py-2 no-scrollbar leading-tight min-h-[34px] max-h-[120px]"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? "Listening..." : (t.inputPlaceholder || "Describe your symptoms in detail...")}
          disabled={disabled || isListening}
          dir={dir} aria-label={t.inputPlaceholder}
          rows={1}
        />
        <div className="composer__actions flex flex-shrink-0">
          <button
            type="button"
            className={`h-9 w-9 rounded-full flex flex-shrink-0 items-center justify-center transition-all duration-300 ${
              value.trim() && !disabled
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                : "bg-white/5 text-slate-500"
            }`}
          onClick={() => {
            if (value.trim()) onSubmit(value.trim());
          }}
          disabled={disabled || !value.trim()}
          title={t.send || "Send"}
        >
          <SendIcon size={16} />
        </button>
        </div>
      </div>
      <p className="text-[10px] text-center text-slate-500 mt-2 font-medium">
        This tool does not provide medical advice or diagnosis. Always consult a qualified physician.
      </p>
    </div>
  );

  });

Composer.displayName = "Composer";
