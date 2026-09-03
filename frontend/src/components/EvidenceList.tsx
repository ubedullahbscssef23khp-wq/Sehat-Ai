import type { Citation, Language, LocalizedText } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { SourceIcon } from "./Icons";

interface EvidenceListProps {
  evidence: Citation[];
  evidenceNote: LocalizedText | null;
  language: Language;
}

function formatDate(value: string, language: Language): string {
  try {
    return new Intl.DateTimeFormat(language, { year: "numeric", month: "short", day: "numeric" }).format(
      new Date(value),
    );
  } catch {
    return value;
  }
}

/** Shows only what the backend returned. Citations are never fabricated, and
 * an empty result is surfaced honestly via the backend's evidence note. */
export function EvidenceList({ evidence, evidenceNote, language }: EvidenceListProps) {
  const t = strings(language);

  if (evidence.length === 0) {
    if (!evidenceNote) {
      return null;
    }
    return (
      <section className="evidence evidence--empty" aria-label={t.evidenceHeading}>
        <p className="evidence__note">{localized(evidenceNote, language)}</p>
      </section>
    );
  }

  return (
    <section className="evidence" aria-label={t.evidenceHeading}>
      <p className="evidence__heading">
        <SourceIcon size={16} />
        <span>{t.evidenceHeading}</span>
      </p>
      <ul className="evidence__list">
        {evidence.map((citation, index) => (
          <li key={index} className="evidence__item">
            <div className="evidence__meta">
              <span className="evidence__source">{citation.source}</span>
              <span className="evidence__date">
                {t.reviewedOn} · {formatDate(citation.date_reviewed, language)}
              </span>
            </div>
            {citation.snippet && <p className="evidence__snippet">{citation.snippet}</p>}
          </li>
        ))}
      </ul>
    </section>
  );
}
