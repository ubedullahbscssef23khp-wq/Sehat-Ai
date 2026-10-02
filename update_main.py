import re
with open("backend/app/main.py", "r") as f:
    content = f.read()

if "from app.api import v1" not in content:
    content = content.replace("from app.api import conversation, health", "from app.api import conversation, health, v1")
    content = content.replace("app.include_router(conversation.router)", "app.include_router(conversation.router)\\n    app.include_router(v1.router)")
    
    with open("backend/app/main.py", "w") as f:
        f.write(content)
