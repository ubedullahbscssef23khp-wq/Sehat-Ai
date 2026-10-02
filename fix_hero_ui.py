import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

# Replace the hero text container layout to add the visual anchor
old_hero_centerpiece = '''        <div className="relative z-10 flex flex-col items-center text-center">
          <div className="mb-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
            <span className="text-xs font-bold tracking-widest uppercase text-cyan-300">AI Health Companion • Triage Ready</span>
          </div>
          
          <h1 id="hero-title" className="text-3xl md:text-5xl font-extrabold text-white tracking-tight leading-tight mb-4">
            Hey, How Can <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Sehat AI</span> Help You?
          </h1>
          
          <p className="text-slate-400 text-sm md:text-base max-w-xl mx-auto mb-10 leading-relaxed">
            Describe your symptoms for instant safety-screened triage and clinician handoff briefs.
          </p>
          
          <button 
            onClick={() => onAction && onAction('start')}
            className="group relative inline-flex items-center justify-center gap-3 px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-2xl font-bold text-lg shadow-[0_10px_25px_rgba(6,182,212,0.35)] hover:shadow-[0_15px_35px_rgba(6,182,212,0.5)] transition-all duration-300 overflow-hidden transform hover:-translate-y-0.5"
          >
            <SparklesIcon size={20} />
            <span>Start Clinical Consultation</span>
            <div className="group-hover:translate-x-1 transition-transform">{arrowSvg}</div>
            
            <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
          </button>
        </div>'''

new_hero_centerpiece = '''        <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-8 md:gap-12 text-center md:text-left">
          <div className="flex-1">
            <div className="mb-6 inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.15)]">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse"></span>
              <span className="text-[10px] md:text-xs font-bold tracking-widest uppercase text-cyan-300">AI Health Companion • Triage Ready</span>
            </div>
            
            <h1 id="hero-title" className="text-3xl md:text-5xl lg:text-6xl font-extrabold text-white tracking-tight leading-tight mb-4">
              Hey, How Can <br className="hidden md:block" /><span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">Sehat AI</span> Help You?
            </h1>
            
            <p className="text-slate-400 text-sm md:text-base max-w-md mx-auto md:mx-0 mb-8 md:mb-10 leading-relaxed">
              Describe your symptoms for instant safety-screened triage and clinician handoff briefs.
            </p>
            
            <button 
              onClick={() => onAction && onAction('start')}
              className="group relative inline-flex items-center justify-center gap-3 px-6 md:px-8 py-3.5 md:py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white rounded-2xl font-bold text-base md:text-lg shadow-[0_10px_25px_rgba(6,182,212,0.35)] hover:shadow-[0_15px_35px_rgba(6,182,212,0.5)] transition-all duration-300 overflow-hidden transform hover:-translate-y-0.5"
            >
              <SparklesIcon size={20} />
              <span>Start Clinical Consultation</span>
              <div className="group-hover:translate-x-1 transition-transform">{arrowSvg}</div>
              
              <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]"></div>
            </button>
          </div>
          
          <div className="hidden md:flex flex-none w-48 h-48 lg:w-64 lg:h-64 relative items-center justify-center">
            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500/20 to-blue-600/30 rounded-full blur-xl border border-cyan-500/30 animate-[pulse_4s_ease-in-out_infinite]"></div>
            <div className="absolute inset-4 bg-[#0f172a]/40 backdrop-blur-md rounded-full border border-white/10 flex items-center justify-center">
               <div className="w-16 h-16 text-cyan-400 animate-[pulse_2s_ease-in-out_infinite]">
                 <SparklesIcon size={64} />
               </div>
            </div>
            {/* Ambient inner ring */}
            <div className="absolute inset-10 border border-cyan-400/20 rounded-full animate-[spin_10s_linear_infinite]"></div>
          </div>
        </div>'''

content = content.replace(old_hero_centerpiece, new_hero_centerpiece)

# Add the inset shadow to the main hero card and bento cards
content = content.replace(
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[32px] p-8 md:p-12 shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)]',
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[32px] p-8 md:p-12 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)]'
)

# Replace the bento grid cards to use the bg-gradient-to-b and inset shadow
old_bento_button_start = 'className="text-left bg-[#121a2f]/60 hover:bg-[#1c2847]/80 backdrop-blur-xl border border-white/10 hover:border-white/20 rounded-[24px] p-6 shadow-[0_10px_30px_-15px_rgba(0,0,0,0.5)] transition-all duration-300 group hover:-translate-y-1"'
new_bento_button_start = 'className="text-left bg-gradient-to-b from-[#162038]/80 to-[#0d1424]/90 hover:from-[#1c2847]/90 hover:to-[#121a2f] backdrop-blur-xl border border-white/10 hover:border-white/20 rounded-[24px] p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_10px_30px_-15px_rgba(0,0,0,0.5)] transition-all duration-300 group hover:-translate-y-1"'

content = content.replace(old_bento_button_start, new_bento_button_start)

# Change the "Or try asking..." section from a column to a grid with distinct badges
old_starters = '''        <div className="flex flex-col gap-3">
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt.key}
              type="button"
              className="flex items-center justify-between px-6 py-4 bg-[#121a2f]/50 hover:bg-[#1c2847]/80 backdrop-blur-xl border border-white/10 hover:border-white/20 rounded-2xl shadow-sm hover:shadow-[0_10px_20px_-10px_rgba(0,0,0,0.5)] transition-all duration-300 group text-left"
              onClick={(e) => {
                e.stopPropagation();
                onStarter(prompt.text[language]);
              }}
            >
              <div className="flex items-center gap-4">
                <div className="text-slate-500 group-hover:text-cyan-400 transition-colors">
                  <InfoIcon size={18} />
                </div>
                <span className="text-slate-200 font-medium group-hover:text-white transition-colors">{prompt.text[language]}</span>
              </div>
              <div className="text-slate-600 group-hover:text-cyan-400 transform translate-x-0 group-hover:translate-x-1 transition-all">
                {arrowSvg}
              </div>
            </button>
          ))}
        </div>'''

new_starters = '''        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-4">
          {STARTER_PROMPTS.map((prompt) => (
            <button
              key={prompt.key}
              type="button"
              className="flex items-center gap-4 px-5 py-4 bg-gradient-to-b from-[#162038]/60 to-[#0d1424]/80 hover:from-[#1c2847]/80 hover:to-[#121a2f] backdrop-blur-xl border border-white/10 hover:border-cyan-500/30 rounded-2xl shadow-[inset_0_1px_0_0_rgba(255,255,255,0.05),0_10px_20px_-10px_rgba(0,0,0,0.5)] transition-all duration-300 group text-left relative overflow-hidden hover:-translate-y-0.5"
              onClick={(e) => {
                e.stopPropagation();
                onStarter(prompt.text[language]);
              }}
            >
              <div className="flex-none w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center group-hover:bg-cyan-500/20 transition-colors shadow-[0_0_10px_rgba(6,182,212,0.1)]">
                <InfoIcon size={18} />
              </div>
              <span className="flex-1 text-slate-300 text-sm font-medium leading-snug group-hover:text-white transition-colors">
                {prompt.text[language]}
              </span>
              <div className="absolute right-4 text-cyan-400 opacity-0 group-hover:opacity-100 transform -translate-x-2 group-hover:translate-x-0 transition-all">
                {arrowSvg}
              </div>
            </button>
          ))}
        </div>'''

content = content.replace(old_starters, new_starters)

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)

