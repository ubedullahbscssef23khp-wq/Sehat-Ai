import type { Language } from "../api/types";
import { LANGUAGES, strings } from "../i18n/strings";

interface LanguagePickerProps {
  language: Language;
  onChange: (language: Language) => void;
  disabled?: boolean;
}

export function LanguagePicker({ language, onChange, disabled }: LanguagePickerProps) {
  const label = strings(language).languageLabel;
  return (
    <label className="lang-picker">
      <span className="lang-picker__label" aria-hidden="true">
        {label}
      </span>
      <select
        className="lang-picker__select"
        aria-label={label}
        value={language}
        disabled={disabled}
        onChange={(event) => {
          const value = event.target.value as Language;
          onChange(value);
        }}
      >
        {LANGUAGES.map((option) => (
          <option key={option.code} value={option.code}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
