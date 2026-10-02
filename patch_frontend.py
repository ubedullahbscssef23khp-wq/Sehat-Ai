import sys
path = 'frontend/src/App.tsx'
content = open(path).read()

new_content = content.replace(
'''          <Composer
            ref={composerRef}
            language={chat.language}
            value={draft}
            disabled={chat.busy}
            onChange={setDraft}
            onSubmit={handleSend}
          />''',
'''          <Composer
            ref={composerRef}
            language={chat.language}
            value={draft}
            disabled={chat.busy || chat.session?.status === "closed"}
            onChange={setDraft}
            onSubmit={handleSend}
          />'''
)
open(path, 'w').write(new_content)
print("patched frontend/src/App.tsx")
