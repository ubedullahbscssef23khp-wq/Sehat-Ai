import type { Language } from "../api/types";
import { strings } from "../i18n/strings";

interface ThinkingIndicatorProps {
  language: Language;
}

export function ThinkingIndicator({ language }: ThinkingIndicatorProps) {
  const t = strings(language);
  return (
    <div className="message message--assistant message--thinking" role="status" aria-live="polite">
      <div className="message__avatar" aria-hidden="true">
        <span className="thinking-dot-row">
          <span className="thinking-dot" />
          <span className="thinking-dot" />
          <span className="thinking-dot" />
        </span>
      </div>
      <div className="message__body">
        <p className="message__author">{t.assistantName}</p>
        <p className="thinking-label">{t.thinking}</p>
      </div>
    </div>
  );
}
