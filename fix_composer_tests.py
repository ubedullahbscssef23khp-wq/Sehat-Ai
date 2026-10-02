with open('frontend/src/components/Composer.tsx', 'r') as f:
    content = f.read()

# Add aria-label to textarea
content = content.replace(
    'dir={dir}\\n          rows={1}', 
    'dir={dir}\\n          aria-label={t.inputPlaceholder}\\n          rows={1}'
)

# Add composer__actions to the Send button container or just the button itself
# The test just queries document.querySelector(".composer__actions")
# Let's wrap the Send button in a div with that class
old_send = '''        <button
          type="button"
          className={`h-9 w-9 rounded-full flex flex-shrink-0 items-center justify-center transition-all duration-300 ${
            value.trim() && !disabled
              ? "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]"
              : "bg-white/5 text-slate-500"
          }`}'''

new_send = '''        <div className="composer__actions flex flex-shrink-0">
          <button
            type="button"
            className={`h-9 w-9 rounded-full flex flex-shrink-0 items-center justify-center transition-all duration-300 ${
              value.trim() && !disabled
                ? "bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                : "bg-white/5 text-slate-500"
            }`}'''

# And add the closing div after the button
content = content.replace(old_send, new_send)
content = content.replace('          <SendIcon size={16} />\n        </button>\n      </div>\n      <p className="text-[10px]', '          <SendIcon size={16} />\n        </button>\n        </div>\n      </div>\n      <p className="text-[10px]')

with open('frontend/src/components/Composer.tsx', 'w') as f:
    f.write(content)

