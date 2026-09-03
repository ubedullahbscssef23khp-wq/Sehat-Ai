import type { Language } from "../api/types";
import { STARTER_PROMPTS, strings } from "../i18n/strings";
import { PulseIcon } from "./Icons";

interface HeroProps {
  language: Language;
  onStarter: (text: string) => void;
}

export function Hero({ language, onStarter }: HeroProps) {
  const t = strings(language);
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero__mark" aria-hidden="true">
        <span className="hero__mark-icon">
          <PulseIcon size={30} />
        </span>
      </div>

      <p className="hero__eyebrow">{t.appName}</p>
      <h1 id="hero-title" className="hero__title">
        {t.heroTitle}
      </h1>
      <p className="hero__subtitle">{t.heroSubtitle}</p>

      <div className="hero__starters">
        <p className="hero__starters-label">{t.starterHeading}</p>
        <div className="hero__starter-grid">
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt.key}
              type="button"
              className="starter-chip"
              onClick={() => onStarter(prompt.text[language])}
            >
              {prompt.text[language]}
            </button>
          ))}
        </div>
      </div>
    </section>
  );
}
