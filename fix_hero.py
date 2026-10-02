import re

with open('frontend/src/components/Hero.tsx', 'r') as f:
    content = f.read()

old_waveform = '''                 {[...Array(5)].map((_, i) => (
                   <div 
                     key={i} 
                     className="w-2 rounded-full bg-gradient-to-t from-cyan-500 to-emerald-400"
                     style={{
                       height: `${20 + Math.random() * 80}%`,
                       animation: `waveform ${1 + Math.random()}s ease-in-out infinite alternate`,
                       animationDelay: `${i * 0.15}s`
                     }}
                   />
                 ))}'''

new_waveform = '''                 {[
                   { h: "60%", dur: "1.2s", del: "0s" },
                   { h: "100%", dur: "1.5s", del: "0.15s" },
                   { h: "40%", dur: "1.1s", del: "0.3s" },
                   { h: "80%", dur: "1.4s", del: "0.45s" },
                   { h: "50%", dur: "1.3s", del: "0.6s" },
                 ].map((bar, i) => (
                   <div 
                     key={i} 
                     className="w-2 rounded-full bg-gradient-to-t from-cyan-500 to-emerald-400"
                     style={{
                       height: bar.h,
                       animation: `waveform ${bar.dur} ease-in-out ${bar.del} infinite alternate`
                     }}
                   />
                 ))}'''

content = content.replace(old_waveform, new_waveform)

with open('frontend/src/components/Hero.tsx', 'w') as f:
    f.write(content)

