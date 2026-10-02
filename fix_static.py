import re

with open('backend/app/main.py', 'r') as f:
    content = f.read()

if 'StaticFiles' not in content:
    content = content.replace('from fastapi.middleware.cors import CORSMiddleware', 'from fastapi.middleware.cors import CORSMiddleware\nfrom fastapi.staticfiles import StaticFiles\nfrom fastapi.responses import FileResponse\nimport os')
    
    mount_code = """    app.include_router(v1.router)

    # Production Static Asset Serving
    dist_path = os.path.join(os.path.dirname(__file__), "..", "..", "dist")
    if os.path.isdir(dist_path):
        app.mount("/assets", StaticFiles(directory=os.path.join(dist_path, "assets")), name="assets")
        
        @app.get("/{catchall:path}", include_in_schema=False)
        def serve_spa(catchall: str):
            # Exclude /api routes from being caught
            if catchall.startswith("api/") or catchall.startswith("v1/"):
                return {"detail": "Not Found"}
            return FileResponse(os.path.join(dist_path, "index.html"))"""

    content = content.replace('    app.include_router(v1.router)', mount_code)
    
    with open('backend/app/main.py', 'w') as f:
        f.write(content)
