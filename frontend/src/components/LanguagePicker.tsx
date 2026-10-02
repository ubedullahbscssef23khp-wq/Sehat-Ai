import type { Language } from "../api/types";
import { LANGUAGES } from "../i18n/strings";

interface LanguagePickerProps {
  language: Language;
  onChange: (language: Language) => void;
  disabled?: boolean;
}

export function LanguagePicker({ language, onChange, disabled }: LanguagePickerProps) {
  return (
    <div className="flex bg-black/40 backdrop-blur-md p-1 rounded-full border border-white/5" role="group" aria-label="Select Language">
      {LANGUAGES.map((option) => (
        <button
          key={option.code}
          type="button"
          disabled={disabled}
          onClick={() => onChange(option.code as Language)}
          className={`relative px-3 py-1.5 text-xs font-bold tracking-wider rounded-full transition-all duration-300 ${
            language === option.code 
              ? 'text-white' 
              : 'text-slate-400 hover:text-white'
          }`}
        >
          {language === option.code && (
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/80 to-blue-600/80 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.4)]" />
          )}
          <span className="relative z-10">{option.code.toUpperCase()}</span>
        </button>
      ))}
    </div>
  );
}
