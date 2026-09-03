import type { GuidanceResponse, Language } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { DisclaimerBlock } from "./DisclaimerBlock";
import { EvidenceList } from "./EvidenceList";
import { FollowUpList } from "./FollowUpList";
import { PulseIcon } from "./Icons";
import { TriageCard } from "./TriageCard";

interface AssistantMessageProps {
  response: GuidanceResponse;
  language: Language;
}

export function AssistantMessage({ response, language }: AssistantMessageProps) {
  const t = strings(language);
  return (
    <div className="message message--assistant">
      <div className="message__avatar" aria-hidden="true">
        <PulseIcon size={18} />
      </div>
      <div className="message__body">
        <p className="message__author">{t.assistantName}</p>
        <article className="card assistant-card">
          <p className="assistant-card__text">{localized(response.user_message, language)}</p>

          <TriageCard decision={response.triage} language={language} />

          <FollowUpList questions={response.follow_up_questions} language={language} />

          <EvidenceList
            evidence={response.evidence}
            evidenceNote={response.evidence_note}
            language={language}
          />

          <DisclaimerBlock disclaimers={response.disclaimers} language={language} />
        </article>
      </div>
    </div>
  );
}
