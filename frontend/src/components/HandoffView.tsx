import { useEffect, useState } from "react";
import { v1GetClinicalSummary } from "../api/client";
import { ClinicianSummaryView } from "./ClinicianSummaryView";
import type { Language, ClinicianSummary } from "../api/types";
import { ShieldCheckIcon } from "./Icons";


interface HandoffViewProps {
  sessionId: string | null;
  language: Language;
}

export function HandoffView({ sessionId, language }: HandoffViewProps) {
  const [summary, setSummary] = useState<ClinicianSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  

  useEffect(() => {
    if (!sessionId) {
      setSummary(null);
      setError(null);
      return;
    }
    setLoading(true);
    setError(null);
    v1GetClinicalSummary(sessionId)
      .then(setSummary)
      .catch((err) => {
        console.error(err);
        setError("Unable to load clinical summary. The session may not have enough data yet.");
      })
      .finally(() => setLoading(false));
  }, [sessionId]);

  if (!sessionId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center h-full min-h-[400px]">
        <div className="w-full max-w-md p-8 rounded-[24px] bg-[#121a2f]/40 border border-white/[0.05] backdrop-blur-xl text-center shadow-[0_20px_40px_-15px_rgba(0,0,0,0.5)]">
          <div className="w-16 h-16 mx-auto bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-center text-emerald-400 mb-6 shadow-[0_0_20px_rgba(16,185,129,0.15)]">
            <ShieldCheckIcon size={32} />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Active Session</h3>
          <p className="text-sm text-slate-400 leading-relaxed">
            Start a symptom triage conversation first to generate a verified SBAR handoff brief for the clinician.
          </p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[400px]">
        <div className="flex items-center gap-3 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-sm font-semibold tracking-wider uppercase">Loading SBAR Data...</span>
        </div>
      </div>
    );
  }

  if (error || !summary) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center h-full min-h-[400px]">
        <div className="w-full max-w-md p-8 rounded-[24px] bg-rose-500/10 border border-rose-500/20 backdrop-blur-xl text-center shadow-[0_20px_40px_-15px_rgba(225,29,72,0.1)]">
          <h3 className="text-lg font-bold text-rose-400 mb-2">Summary Not Available</h3>
          <p className="text-sm text-rose-200/70 leading-relaxed">
            {error || "No verified clinical summary is available for this session yet. Continue the triage."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mx-auto py-4">
      <ClinicianSummaryView summary={summary} language={language} />
    </div>
  );
}
