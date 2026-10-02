import re
with open('frontend/src/App.tsx', 'r') as f:
    c = f.read()

c = re.sub(
    r'<HistoryView\s+language=\{chat\.language\}\s+onDelete=\{remove\}\s+/>',
    '<HistoryView language={chat.language} history={history} onLoadSession={handleLoadSession} onDelete={remove} />',
    c
)

with open('frontend/src/App.tsx', 'w') as f:
    f.write(c)
