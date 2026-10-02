import type { GuidanceResponse, Language } from "../api/types";
import { localized } from "../api/types";
import { strings } from "../i18n/strings";
import { ClinicianSummaryView } from "./ClinicianSummaryView";
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
  const isRtl = language === 'ur' || language === 'sd';

  return (
    <div className={`flex w-full mb-8 ${isRtl ? 'flex-row-reverse' : 'flex-row'}`} dir={isRtl ? 'rtl' : 'ltr'}>
      <div className={`flex-none w-10 h-10 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.15)] ${isRtl ? 'ml-4' : 'mr-4'} mt-1`}>
        <PulseIcon size={20} />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-cyan-400 mb-2 tracking-wide uppercase">{t.assistantName}</p>
        <article className="bg-[#121a2f]/80 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)] p-5 md:p-6 flex flex-col gap-5 overflow-hidden">
          <TriageCard decision={response.triage} language={language} />
          
          {response.user_message && (
            <p className="text-slate-200 text-[15px] leading-relaxed">
              {localized(response.user_message, language)}
            </p>
          )}
          
          {response.follow_up_questions && response.follow_up_questions.length > 0 && (
            <FollowUpList questions={response.follow_up_questions} language={language} />
          )}
          
          {response.disclaimers && response.disclaimers.length > 0 && (
            <DisclaimerBlock disclaimers={response.disclaimers} language={language} />
          )}
          
          {response.evidence && response.evidence.length > 0 && (
            <EvidenceList
              evidence={response.evidence}
              evidenceNote={response.evidence_note}
              language={language}
            />
          )}
          
          {response.clinician_summary && (
            <ClinicianSummaryView summary={response.clinician_summary} language={language} />
          )}
        </article>
      </div>
    </div>
  );
}
