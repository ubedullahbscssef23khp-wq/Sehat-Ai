import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

# Replace Tile A icon container with a circular progress meter SVG
old_tile_a_icon = '''          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:bg-cyan-500/20 transition-all">
            <SparklesIcon size={24} />
          </div>'''

new_tile_a_icon = '''          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:bg-cyan-500/20 transition-all relative">
            <svg viewBox="0 0 36 36" className="w-8 h-8 transform -rotate-90">
              <path className="text-cyan-500/20" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
              <path className="text-cyan-400 animate-[dash_2s_ease-out_forwards]" strokeDasharray="100, 100" strokeDashoffset="25" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="currentColor" strokeWidth="3" />
            </svg>
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-[10px] font-bold text-cyan-300">75%</span>
            </div>
          </div>'''

content = content.replace(old_tile_a_icon, new_tile_a_icon)

# Update Tile C sparkline with glowing cyan markers
old_tile_c_icon = '''          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all overflow-hidden relative">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="absolute group-hover:animate-[pulse_1.5s_ease-in-out_infinite]"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>
          </div>'''

new_tile_c_icon = '''          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-5 group-hover:scale-110 group-hover:bg-blue-500/20 transition-all overflow-hidden relative">
            <svg width="28" height="20" viewBox="0 0 28 20" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="absolute group-hover:animate-[pulse_1.5s_ease-in-out_infinite]">
              <path d="M2 10 L8 10 L11 4 L17 16 L20 10 L26 10" className="text-blue-400" />
              <circle cx="11" cy="4" r="2.5" className="fill-cyan-400 animate-pulse drop-shadow-[0_0_5px_rgba(6,182,212,1)]" stroke="none" />
              <circle cx="17" cy="16" r="2.5" className="fill-cyan-400 animate-pulse drop-shadow-[0_0_5px_rgba(6,182,212,1)]" stroke="none" style={{animationDelay: '0.5s'}} />
            </svg>
          </div>'''

content = content.replace(old_tile_c_icon, new_tile_c_icon)

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)

