import re

with open('backend/app/main.py', 'r') as f:
    content = f.read()

if 'SecurityHeadersMiddleware' not in content:
    csp_middleware = """class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Content-Type-Options", "nosniff")
                headers.append("X-Frame-Options", "DENY")
                headers.append("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
                headers.append("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' https://generativelanguage.googleapis.com;")
            await send(message)

        await self.app(scope, receive, send_with_headers)
"""
    # Insert before def create_app
    content = content.replace("def create_app(", csp_middleware + "\n\ndef create_app(")
    # Insert middleware registration
    content = content.replace("app.add_middleware(RequestIdMiddleware)", "app.add_middleware(RequestIdMiddleware)\n    app.add_middleware(SecurityHeadersMiddleware)")

    with open('backend/app/main.py', 'w') as f:
        f.write(content)
