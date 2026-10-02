import re

content = """import { useState } from "react";
import type { ClinicianSummary, Language } from "../api/types";
import { strings } from "../i18n/strings";
import { AlertIcon, PulseIcon, ShieldIcon, CopyIcon, PrintIcon, CheckIcon } from "./Icons";

interface ClinicianSummaryViewProps {
  summary: ClinicianSummary;
  language: Language;
}

export function ClinicianSummaryView({ summary, language }: ClinicianSummaryViewProps) {
  const t = strings(language);
  const { structured_case, fired_rules, triage_decision, timeline } = summary;
  const [copied, setCopied] = useState(false);

  const hasSymptoms = structured_case.symptoms && structured_case.symptoms.length > 0;
  const hasAge = Boolean(
    structured_case.demographics?.age_group && structured_case.demographics.age_group !== "unknown",
  );
  const hasPregnancy =
    structured_case.demographics?.pregnant !== null &&
    structured_case.demographics?.pregnant !== undefined;
  const hasDemographics = hasAge || hasPregnancy;
  const hasRedFlags =
    structured_case.red_flag_signals && structured_case.red_flag_signals.length > 0;
  const hasFiredRules = fired_rules && fired_rules.length > 0;
  const hasTimeline = timeline && timeline.length > 0;

  const handleCopy = async () => {
    try {
      const text = formatHandoff(summary, t);
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (e) {
      console.error("Clipboard write failed", e);
    }
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <details className="clinician-summary clinician-summary--printable">
      <summary className="clinician-summary__summary">
        <span className="clinician-summary__icon" aria-hidden="true">
          <PulseIcon size={16} />
        </span>
        <span className="clinician-summary__title">{t.clinicianSummaryHeading}</span>
        <span className="clinician-summary__badge">{t.clinicianSummaryBadge}</span>
      </summary>
      
      <div className="clinician-summary__content">
        <div className="clinician-summary__handoff-actions no-print">
          <button 
            type="button" 
            className="clinician-summary__action-btn"
            onClick={handleCopy}
            aria-label={t.copyHandoff}
          >
            {copied ? <CheckIcon size={14} /> : <CopyIcon size={14} />}
            <span>{copied ? t.copySuccess : t.copyHandoff}</span>
          </button>
          <button 
            type="button" 
            className="clinician-summary__action-btn"
            onClick={handlePrint}
            aria-label={t.printHandoff}
          >
            <PrintIcon size={14} />
            <span>{t.printHandoff}</span>
          </button>
        </div>

        <div className="clinician-summary__print-header only-print">
          <h2>{t.handoffTitle}</h2>
          <p><strong>{t.handoffDisclaimer1}</strong></p>
          <p>{t.handoffDisclaimer2}</p>
        </div>

        {structured_case.chief_complaint && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">{t.chiefComplaintLabel}</h4>
            <p className="clinician-summary__text">{structured_case.chief_complaint}</p>
          </div>
        )}

        {triage_decision && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">{t.triageDecisionLabel}</h4>
            <span
              className={`clinician-summary__triage-badge clinician-summary__triage-badge--${triage_decision.level}`}
            >
              {t.triageLabels[triage_decision.level]}
            </span>
          </div>
        )}

        {hasSymptoms && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">{t.symptomsLabel}</h4>
            <ul className="clinician-summary__symptom-list">
              {structured_case.symptoms.map((symptom, idx) => (
                <li key={idx} className="clinician-summary__symptom-item">
                  <span className="clinician-summary__symptom-name">{symptom.name}</span>
                  <div className="clinician-summary__symptom-details">
                    {symptom.severity !== null && (
                      <span className="clinician-summary__tag">
                        {t.severityLabel}: {symptom.severity}/10
                      </span>
                    )}
                    {symptom.duration && (
                      <span className="clinician-summary__tag">
                        {t.durationLabel}: {symptom.duration}
                      </span>
                    )}
                    {symptom.progression && symptom.progression !== "unknown" && (
                      <span className="clinician-summary__tag">
                        {t.progressionLabel}: {symptom.progression}
                      </span>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}

        {hasDemographics && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">{t.demographicsLabel}</h4>
            <div className="clinician-summary__tags">
              {hasAge && (
                <span className="clinician-summary__tag">
                  {t.ageGroupLabel}: {structured_case.demographics.age_group}
                </span>
              )}
              {hasPregnancy && (
                <span className="clinician-summary__tag">
                  {t.pregnancyLabel}:{" "}
                  {structured_case.demographics.pregnant ? t.pregnantYes : t.pregnantNo}
                </span>
              )}
            </div>
          </div>
        )}

        {hasRedFlags && (
          <div className="clinician-summary__section clinician-summary__section--alert">
            <h4 className="clinician-summary__section-title">
              <AlertIcon size={14} />
              <span>{t.redFlagsLabel}</span>
            </h4>
            <ul className="clinician-summary__signal-list">
              {structured_case.red_flag_signals.map((signal, idx) => (
                <li key={idx} className="clinician-summary__signal-item">
                  {signal}
                </li>
              ))}
            </ul>
          </div>
        )}

        {hasFiredRules && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">
              <ShieldIcon size={14} />
              <span>{t.firedRulesLabel}</span>
            </h4>
            <ul className="clinician-summary__rule-list">
              {fired_rules.map((rule, idx) => (
                <li key={idx} className="clinician-summary__rule-item">
                  <span className="clinician-summary__rule-desc">{rule.description}</span>
                  {rule.level && (
                    <span className="clinician-summary__rule-level">
                      {rule.level.toUpperCase()}
                    </span>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}

        {hasTimeline && (
          <div className="clinician-summary__section">
            <h4 className="clinician-summary__section-title">{t.timelineLabel}</h4>
            <ol className="clinician-summary__timeline-list">
              {timeline.map((entry, idx) => (
                <li key={idx} className="clinician-summary__timeline-item">
                  {entry}
                </li>
              ))}
            </ol>
          </div>
        )}
        
        <div className="clinician-summary__print-footer only-print">
          <p>{t.handoffFooter}</p>
        </div>
      </div>
    </details>
  );
}

function formatHandoff(summary: ClinicianSummary, t: ReturnType<typeof strings>): string {
  const { structured_case, fired_rules, triage_decision, timeline, generated_at, model_attribution } = summary;
  
  const lines: string[] = [];
  
  lines.push(t.handoffTitle);
  lines.push("");
  lines.push(t.handoffDisclaimer1);
  lines.push(t.handoffDisclaimer2);
  lines.push("");
  
  lines.push(`${t.chiefComplaintLabel}:`);
  lines.push(structured_case.chief_complaint || t.notProvided);
  lines.push("");
  
  lines.push(`${t.symptomsLabel}:`);
  if (structured_case.symptoms && structured_case.symptoms.length > 0) {
    for (const sym of structured_case.symptoms) {
      lines.push(`- ${sym.name}`);
      if (sym.severity !== null) {
        lines.push(`  ${t.severityLabel}: ${sym.severity}/10`);
      }
      if (sym.duration) {
        lines.push(`  ${t.durationLabel}: ${sym.duration}`);
      }
      if (sym.progression && sym.progression !== "unknown") {
        lines.push(`  ${t.progressionLabel}: ${sym.progression}`);
      }
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.demographicsLabel}:`);
  const hasAge = structured_case.demographics?.age_group && structured_case.demographics.age_group !== "unknown";
  const hasPregnancy = structured_case.demographics?.pregnant !== null && structured_case.demographics?.pregnant !== undefined;
  
  if (hasAge || hasPregnancy) {
    if (hasAge) lines.push(`- ${t.ageGroupLabel}: ${structured_case.demographics.age_group}`);
    if (hasPregnancy) lines.push(`- ${t.pregnancyLabel}: ${structured_case.demographics.pregnant ? t.pregnantYes : t.pregnantNo}`);
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.redFlagsLabel}:`);
  if (structured_case.red_flag_signals && structured_case.red_flag_signals.length > 0) {
    for (const signal of structured_case.red_flag_signals) {
      lines.push(`- ${signal}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.firedRulesLabel}:`);
  if (fired_rules && fired_rules.length > 0) {
    for (const rule of fired_rules) {
      lines.push(`- ${rule.description}${rule.level ? ` (${rule.level.toUpperCase()})` : ""}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.triageDecisionLabel}:`);
  if (triage_decision && triage_decision.level) {
    lines.push(t.triageLabels[triage_decision.level]);
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  lines.push(`${t.timelineLabel}:`);
  if (timeline && timeline.length > 0) {
    for (const entry of timeline) {
      lines.push(`- ${entry}`);
    }
  } else {
    lines.push(t.notProvided);
  }
  lines.push("");
  
  if (generated_at) {
    lines.push(`${t.generatedLabel}:`);
    lines.push(generated_at);
    lines.push("");
  }
  
  if (model_attribution) {
    lines.push(`${t.modelAttributionLabel}:`);
    lines.push(model_attribution);
    lines.push("");
  }
  
  lines.push(t.handoffFooter);
  
  return lines.join("\\n");
}
"""

with open("frontend/src/components/ClinicianSummaryView.tsx", "w") as f:
    f.write(content)

