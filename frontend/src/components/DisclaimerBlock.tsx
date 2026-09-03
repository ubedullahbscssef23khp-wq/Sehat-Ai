import type { Language, LocalizedText } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { ShieldIcon } from "./Icons";

interface DisclaimerBlockProps {
  disclaimers: LocalizedText[];
  language: Language;
}

/** Server-injected mandatory disclaimers, rendered verbatim. The frontend can
 * display them but has no code path that removes or hides them. */
export function DisclaimerBlock({ disclaimers, language }: DisclaimerBlockProps) {
  if (disclaimers.length === 0) {
    return null;
  }
  const t = strings(language);
  return (
    <section className="disclaimer" aria-label={t.disclaimerHeading}>
      <p className="disclaimer__heading">
        <ShieldIcon size={15} />
        <span>{t.disclaimerHeading}</span>
      </p>
      {disclaimers.map((disclaimer, index) => (
        <p key={index} className="disclaimer__text">
          {localized(disclaimer, language)}
        </p>
      ))}
    </section>
  );
}
