import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

# I will replace the entire return block in Hero.tsx
new_return = '''  return (
    <div className="flex-1 flex flex-col min-h-0 overflow-y-auto space-y-6 pr-2 no-scrollbar animate-fade-in relative z-10">
      {/* 1. Hero AI Interactive Card (Balanced Scale) */}
      <div className="rounded-[24px] p-6 bg-[#121a2f]/70 border border-white/[0.08] backdrop-blur-xl shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)] relative overflow-hidden flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-3 max-w-lg z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-xs font-semibold tracking-wide">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
            AI HEALTH COMPANION • TRIAGE VERIFIED
          </div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-white leading-snug">
            Hey, How Can <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Sehat AI</span> Help You?
          </h2>
          <p className="text-xs md:text-sm text-slate-300 leading-relaxed">
            Describe your symptoms for instant safety-screened triage and structured clinician handoff briefs.
          </p>
        </div>

        {/* Integrated Audio Visualizer Disc */}
        <div className="relative flex-shrink-0 w-28 h-28 rounded-full bg-gradient-to-b from-cyan-500/10 to-blue-600/5 border border-cyan-500/20 flex items-center justify-center shadow-[0_0_30px_rgba(6,182,212,0.15)]">
          <div className="flex items-center gap-1.5 h-10">
            <span className="w-1.5 h-6 bg-cyan-400 rounded-full animate-pulse" />
            <span className="w-1.5 h-10 bg-cyan-300 rounded-full animate-pulse" style={{ animationDelay: '150ms' }} />
            <span className="w-1.5 h-7 bg-emerald-400 rounded-full animate-pulse" style={{ animationDelay: '300ms' }} />
            <span className="w-1.5 h-4 bg-cyan-400 rounded-full animate-pulse" style={{ animationDelay: '450ms' }} />
          </div>
        </div>
      </div>

      {/* 2. Bento Quick Action Grid (2 Columns) */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div 
          onClick={() => onAction && onAction('start')}
          className="rounded-[20px] p-5 bg-[#121a2f]/60 border border-white/[0.08] backdrop-blur-xl hover:border-cyan-500/30 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="p-2 rounded-xl bg-blue-500/15 text-blue-400 text-sm">✦</span>
            <span className="text-[11px] font-semibold text-cyan-400 uppercase tracking-wider">Triage</span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">Active Symptom Check</h3>
          <p className="text-xs text-slate-400 mt-1">Interactive step-by-step diagnostic triage questionnaire.</p>
        </div>

        <div 
          onClick={() => onAction && onAction('handoff')}
          className="rounded-[20px] p-5 bg-[#121a2f]/60 border border-white/[0.08] backdrop-blur-xl hover:border-emerald-500/30 transition-all cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-3">
            <span className="p-2 rounded-xl bg-emerald-500/15 text-emerald-400 text-sm">⇗</span>
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">Summary</span>
          </div>
          <h3 className="text-sm font-bold text-white group-hover:text-emerald-300 transition-colors">Clinician Handoff (SBAR)</h3>
          <p className="text-xs text-slate-400 mt-1">Review verified transfer brief ready for physician handoff.</p>
        </div>
      </div>

      {/* 3. Starter Prompt Chips (Compact 3-Row Grid) */}
      <div className="space-y-2 pt-1">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider px-1">Common Consultations</span>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {STARTER_PROMPTS.map((prompt, i) => (
            <button 
              key={prompt.key} 
              onClick={() => onStarter(prompt.text[language])}
              className="p-3.5 rounded-[16px] bg-[#121a2f]/40 border border-white/[0.06] hover:border-cyan-500/30 hover:bg-[#16203a]/60 text-left transition-all text-xs text-slate-200 flex items-center justify-between group"
            >
              <span className="truncate pr-2">{prompt.text[language]}</span>
              <span className="text-slate-500 group-hover:text-cyan-400">→</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}'''

# Extract up to "return ("
head_match = re.search(r'(.*?)(?=  return \()', content, re.DOTALL)
if head_match:
    new_content = head_match.group(1) + new_return
    with open('frontend/src/components/Hero.tsx', 'w') as f:
        f.write(new_content)
