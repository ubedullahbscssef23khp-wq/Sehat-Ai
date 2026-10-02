import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

old_hero_anchor = '''            <div className="absolute inset-4 bg-[#0f172a]/40 backdrop-blur-md rounded-full border border-white/10 flex items-center justify-center">
               <div className="w-16 h-16 text-cyan-400 animate-[pulse_2s_ease-in-out_infinite]">
                 <SparklesIcon size={64} />
               </div>
            </div>'''

new_hero_anchor = '''            <div className="absolute inset-4 bg-[#0f172a]/40 backdrop-blur-md rounded-full border border-white/10 flex items-center justify-center overflow-hidden">
               <div className="flex items-center gap-1.5 h-16">
                 {[...Array(5)].map((_, i) => (
                   <div 
                     key={i} 
                     className="w-2 rounded-full bg-gradient-to-t from-cyan-500 to-emerald-400"
                     style={{
                       height: `${20 + Math.random() * 80}%`,
                       animation: `waveform ${1 + Math.random()}s ease-in-out infinite alternate`,
                       animationDelay: `${i * 0.15}s`
                     }}
                   />
                 ))}
               </div>
            </div>'''

content = content.replace(old_hero_anchor, new_hero_anchor)

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)

