import re

with open('frontend/src/App.tsx', 'r') as f:
    content = f.read()

# Replace custom-scrollbar with no-scrollbar
content = content.replace('custom-scrollbar', 'no-scrollbar')

# Add shadow inset to the main content area and sidebar
content = content.replace(
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)] p-4"',
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)] p-4"'
)

content = content.replace(
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[0_20px_40px_-15px_rgba(0,0,0,0.7)] overflow-hidden relative"',
    'bg-[#121a2f]/70 backdrop-blur-2xl border border-white/10 rounded-[24px] shadow-[inset_0_1px_0_0_rgba(255,255,255,0.1),0_20px_40px_-15px_rgba(0,0,0,0.7)] overflow-hidden relative"'
)

# Update sidebar bottom text to include deterministic mode
content = content.replace(
    '<p className="text-xs text-slate-400 text-center uppercase tracking-widest font-semibold">Assist, don\'t diagnose</p>',
    '''<p className="text-[10px] text-slate-400 text-center uppercase tracking-widest font-semibold mb-1">Assist, don't diagnose</p>
              <div className="flex items-center justify-center gap-1.5 mt-2 pt-2 border-t border-white/10">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)]"></span>
                <span className="text-[10px] text-cyan-300/80 font-mono tracking-wider">CLINICAL MODE: DETERMINISTIC</span>
              </div>'''
)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(content)
