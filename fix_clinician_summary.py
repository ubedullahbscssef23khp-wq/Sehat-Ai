import re

content = '''import type { ClinicianSummary, Language } from "../api/types";
import { CopyIcon, PrintIcon, ShieldCheckIcon } from "./Icons";
import { strings, directionOf } from "../i18n/strings";

interface ClinicianSummaryProps {
  summary: ClinicianSummary;
  language: Language;
}

export function ClinicianSummaryView({ summary, language }: ClinicianSummaryProps) {
  const t = strings(language);
  const dir = directionOf(language);

  const handleCopy = () => {
    const text = `SITUATION:
${summary.structured_case.chief_complaint}
BACKGROUND:
${summary.structured_case.symptoms.map(s => s.name).join(", ")}
ASSESSMENT:
Severity: ${summary.triage_decision.level}
RECOMMENDATION:
${summary.triage_decision.next_actions.map((n) => n.en).join(", ")}
    `.trim();
    navigator.clipboard.writeText(text);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="mt-4 flex flex-col gap-0" dir={dir}>
      {/* 3D Stack Base container */}
      <div className="relative z-30 bg-gradient-to-b from-[#162038] to-[#0d1424] border border-white/10 rounded-[24px] p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)]">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 pb-4 mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shadow-[0_0_15px_rgba(16,185,129,0.15)]">
              <ShieldCheckIcon size={20} />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.8)]"></span>
                <span className="text-[10px] font-bold tracking-widest uppercase text-emerald-400">Deterministic SBAR Ready</span>
              </div>
              <h2 className="text-lg font-bold text-white">{t.clinicianSummaryLabel}</h2>
            </div>
          </div>
        </div>

        {/* Export Controls */}
        <div className="flex flex-wrap gap-3 mb-6">
          <button onClick={handleCopy} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/20 text-emerald-400 text-sm font-semibold transition-all hover:shadow-[0_0_15px_rgba(16,185,129,0.2)]">
            <CopyIcon size={16} /> Copy Brief
          </button>
          <button onClick={handlePrint} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 text-sm font-semibold transition-all">
            <PrintIcon size={16} /> Export Verified SBAR
          </button>
        </div>

        {/* Top Level Content (SBAR) */}
        <div className="flex flex-col gap-4">
          <div className="bg-black/20 rounded-xl p-4 border border-white/5">
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">Situation (Chief Complaint)</h4>
            <p className="text-slate-200 text-[15px] leading-relaxed">{summary.structured_case.chief_complaint}</p>
          </div>
          
          {summary.structured_case.symptoms && summary.structured_case.symptoms.length > 0 && (
            <div className="bg-black/20 rounded-xl p-4 border border-white/5">
              <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2">Background (Symptoms)</h4>
              <ul className="list-disc list-inside text-slate-300 text-[14px] space-y-1">
                {summary.structured_case.symptoms.map((s, i) => (
                  <li key={i}>{s.name} {s.severity !== null && `(Sev: ${s.severity})`} {s.duration && `[${s.duration}]`}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Layer 2: Safety Signals (Red Flags / Fired Rules) */}
      {((summary.structured_case.red_flag_signals && summary.structured_case.red_flag_signals.length > 0) || (summary.fired_rules && summary.fired_rules.length > 0)) && (
        <div className="relative z-20 -mt-6 mx-4 bg-[#1a1114]/90 backdrop-blur-xl border border-rose-500/20 rounded-b-[20px] pt-10 pb-5 px-6 shadow-[0_15px_30px_-10px_rgba(0,0,0,0.5)]">
          <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-3">Safety Signals & Alerts</h4>
          <ul className="list-disc list-inside text-rose-200/80 text-[14px] space-y-1">
            {summary.structured_case.red_flag_signals?.map((s, i) => (
              <li key={`rf-${i}`}>{s}</li>
            ))}
            {summary.fired_rules?.map((r, i) => (
              <li key={`rule-${i}`}>{r.description} ({r.level})</li>
            ))}
          </ul>
        </div>
      )}

      {/* Layer 3: Demographics & Timeline */}
      {((summary.structured_case.demographics.age_group || summary.structured_case.demographics.pregnant !== null) || (summary.timeline && summary.timeline.length > 0)) && (
        <div className="relative z-10 -mt-6 mx-8 bg-[#121a2f]/80 backdrop-blur-xl border border-white/5 rounded-b-[16px] pt-10 pb-5 px-6 shadow-[0_15px_30px_-10px_rgba(0,0,0,0.4)]">
          {summary.timeline && summary.timeline.length > 0 && (
            <div className="mb-3">
              <h4 className="text-xs font-bold text-amber-400/80 uppercase tracking-wider mb-2">Timeline</h4>
              <ul className="list-disc list-inside text-slate-400 text-[13px] space-y-1">
                {summary.timeline.map((tItem, i) => (
                  <li key={i}>{tItem}</li>
                ))}
              </ul>
            </div>
          )}
          {(summary.structured_case.demographics.age_group || summary.structured_case.demographics.pregnant !== null) && (
            <div>
              <h4 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Demographics</h4>
              <p className="text-slate-400 text-[13px]">
                Age: {summary.structured_case.demographics.age_group || 'Unknown'} 
                {summary.structured_case.demographics.pregnant === true && " • Pregnant"}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
'''

with open('frontend/src/components/ClinicianSummaryView.tsx', 'w') as f:
    f.write(content)

