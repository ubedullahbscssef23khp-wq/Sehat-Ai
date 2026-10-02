import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

# Add a third Bento Tile for Activity & Session Telemetry (Compact SVG sparkline wave with glowing cyan data markers)
old_bento_grid_start = '<div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">'
new_bento_grid_start = '<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-6">'

content = content.replace(old_bento_grid_start, new_bento_grid_start)

# Add the 3rd tile just before the "Or try asking..." section
bento_tile_3 = '''        <button 
          onClick={() => onAction && onAction('history')}
          className="text-left bg-gradient-to-b from-[#162038]/80 to-[#0d1424]/90 hover:from-[#1c2847]/90 hover:to-[#121a2f] backdrop-blur-xl border border-white/10 hover:border-white/20 rounded-[24px] p-6 shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_10px_30px_-15px_rgba(0,0,0,0.5)] transition-all duration-300 group hover:-translate-y-1"
        >
          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all overflow-hidden relative">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute group-hover:animate-[pulse_1.5s_ease-in-out_infinite]"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>
          <h3 className="text-xl font-bold text-white mb-2 group-hover:text-blue-300 transition-colors">Activity Telemetry</h3>
          <p className="text-slate-400 text-sm leading-relaxed mb-4">View session metrics and historical triage data.</p>
          <div className="flex items-center text-blue-400 text-sm font-semibold gap-1 opacity-0 group-hover:opacity-100 transform -translate-x-2 group-hover:translate-x-0 transition-all">
            Open Logs {arrowSvg}
          </div>
        </button>
      </div>'''

content = content.replace('      </div>\n      {/* "OR TRY ASKING..." SECTION */}', bento_tile_3 + '\n      {/* "OR TRY ASKING..." SECTION */}')

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)

