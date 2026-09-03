import { forwardRef, useCallback, useEffect } from "react";
import type { KeyboardEvent } from "react";
import type { Language } from "../api/types";
import { strings } from "../i18n/strings";
import { SendIcon } from "./Icons";

// Mirrors the backend default `sehat_max_message_chars`; the server remains the
// authority and returns a friendly `message_too_long` error if exceeded.
const MAX_MESSAGE_CHARS = 2000;

interface ComposerProps {
  language: Language;
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
  onSubmit: (value: string) => void;
}

export const Composer = forwardRef<HTMLTextAreaElement, ComposerProps>(function Composer(
  { language, value, disabled, onChange, onSubmit },
  ref,
) {
  const t = strings(language);
  const canSend = value.trim().length > 0 && !disabled;

  // Grows the textarea to fit its content within a sane cap.
  const autosize = useCallback((element: HTMLTextAreaElement | null) => {
    if (!element) return;
    element.style.height = "auto";
    const next = Math.min(element.scrollHeight, 180);
    element.style.height = `${next}px`;
  }, []);

  useEffect(() => {
    if (ref && typeof ref === "object" && ref.current) {
      autosize(ref.current);
    }
  }, [value, ref, autosize]);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (canSend) {
        onSubmit(value);
      }
    }
  };

  return (
    <form
      className="composer"
      onSubmit={(event) => {
        event.preventDefault();
        if (canSend) onSubmit(value);
      }}
    >
      <div className="composer__field">
        <textarea
          ref={ref}
          className="composer__input"
          rows={1}
          value={value}
          maxLength={MAX_MESSAGE_CHARS}
          placeholder={t.inputPlaceholder}
          aria-label={t.inputPlaceholder}
          disabled={disabled}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button
          type="submit"
          className="composer__send"
          aria-label={t.send}
          disabled={!canSend}
        >
          <SendIcon size={19} />
        </button>
      </div>
    </form>
  );
});
