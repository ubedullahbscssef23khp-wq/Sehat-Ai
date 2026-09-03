import type { Language, TriageDecision, TriageLevel } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { AlertIcon, InfoIcon } from "./Icons";

const LEVEL_CLASS: Record<TriageLevel, string> = {
  emergency: "triage--emergency",
  urgent_same_day: "triage--urgent",
  routine: "triage--routine",
  self_care: "triage--selfcare",
  needs_more_info: "triage--info",
};

interface TriageCardProps {
  decision: TriageDecision;
  language: Language;
}

/** Renders the backend's authoritative triage decision. The frontend never
 * computes, upgrades, or softens the level — it only presents it. Internal
 * identifiers (rule IDs, hashes) are deliberately not displayed. */
export function TriageCard({ decision, language }: TriageCardProps) {
  const t = strings(language);
  const elevated = decision.level === "emergency" || decision.level === "urgent_same_day";

  return (
    <section className={`triage ${LEVEL_CLASS[decision.level]}`} aria-label={t.triageLabels[decision.level]}>
      <header className="triage__head">
        <span className="triage__icon" aria-hidden="true">
          {elevated ? <AlertIcon size={18} /> : <InfoIcon size={18} />}
        </span>
        <h3 className="triage__level">{t.triageLabels[decision.level]}</h3>
      </header>

      <ul className="triage__actions">
        {decision.next_actions.map((action, index) => (
          <li key={index}>{localized(action, language)}</li>
        ))}
      </ul>

      {decision.self_care_limits.length > 0 && (
        <ul className="triage__limits">
          {decision.self_care_limits.map((limit, index) => (
            <li key={index}>{localized(limit, language)}</li>
          ))}
        </ul>
      )}

      {decision.recheck_advice && (
        <p className="triage__recheck">{localized(decision.recheck_advice, language)}</p>
      )}

      {decision.limited_confidence && (
        <p className="triage__limited">
          <InfoIcon size={15} />
          <span>{t.limitedConfidence}</span>
        </p>
      )}
    </section>
  );
}
