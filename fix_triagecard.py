import re

with open('frontend/src/components/TriageCard.tsx', 'r') as f:
    content = f.read()

# Replace the emergency class with the coral/red tailwind card
old_render = '''  return (
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
  );'''

new_render = '''  const isEmergency = decision.level === "emergency";
  
  if (isEmergency) {
    return (
      <div className={`triage ${LEVEL_CLASS[decision.level]} bg-rose-500/10 border-l-4 border-rose-500 rounded-r-2xl p-5 mb-4 shadow-[0_10px_20px_-10px_rgba(225,29,72,0.3)]`} aria-label={t.triageLabels[decision.level]}>
        <div className="flex items-center gap-3 mb-3 text-rose-500">
          <AlertIcon size={24} />
          <h3 className="font-bold text-lg">{t.triageLabels[decision.level]}</h3>
        </div>
        <ul className="list-disc list-inside space-y-2 text-rose-200 font-medium mb-3">
          {decision.next_actions.map((action, index) => (
            <li key={index}>{localized(action, language)}</li>
          ))}
        </ul>
        {decision.self_care_limits.length > 0 && (
          <div className="mt-3 p-3 bg-black/20 rounded-xl border border-rose-500/20">
            <h4 className="text-xs font-bold text-rose-400 uppercase tracking-wider mb-2">Safety Limits</h4>
            <ul className="list-disc list-inside text-rose-200/80 text-sm space-y-1">
              {decision.self_care_limits.map((limit, index) => (
                <li key={index}>{localized(limit, language)}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }

  return (
    <section className={`triage ${LEVEL_CLASS[decision.level]} bg-[#1a2235]/80 border border-white/10 rounded-2xl p-5 shadow-lg`} aria-label={t.triageLabels[decision.level]}>
      <header className="flex items-center gap-2 mb-3">
        <span className={`flex items-center justify-center w-8 h-8 rounded-full ${elevated ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'}`} aria-hidden="true">
          {elevated ? <AlertIcon size={16} /> : <InfoIcon size={16} />}
        </span>
        <h3 className="font-bold text-white text-md">{t.triageLabels[decision.level]}</h3>
      </header>
      <ul className="list-disc list-inside space-y-1 text-slate-300 text-sm">
        {decision.next_actions.map((action, index) => (
          <li key={index}>{localized(action, language)}</li>
        ))}
      </ul>
      {decision.self_care_limits.length > 0 && (
        <ul className="list-disc list-inside space-y-1 text-slate-400 text-sm mt-3 border-t border-white/10 pt-3">
          {decision.self_care_limits.map((limit, index) => (
            <li key={index}>{localized(limit, language)}</li>
          ))}
        </ul>
      )}
      {decision.recheck_advice && (
        <p className="text-amber-400/90 text-sm mt-3 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">{localized(decision.recheck_advice, language)}</p>
      )}
      {decision.limited_confidence && (
        <p className="flex items-center gap-2 text-slate-400 text-xs mt-3">
          <InfoIcon size={14} />
          <span>{t.limitedConfidence}</span>
        </p>
      )}
    </section>
  );'''

content = content.replace(old_render, new_render)

with open('frontend/src/components/TriageCard.tsx', 'w') as f:
    f.write(content)

