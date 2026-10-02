# Stage 1: Build Frontend (Vite)
FROM node:20-alpine AS builder
WORKDIR /app
# Copy package.json and install deps
COPY package*.json ./
COPY frontend/package*.json ./frontend/
RUN npm install --prefix frontend
# Copy source and build
COPY frontend/ ./frontend/
RUN npm run build --prefix frontend

# Stage 2: Production Backend (FastAPI)
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    SEHAT_ENV=production

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/pyproject.toml ./backend/
# Simulating a pip install step from pyproject (for a real deploy, we'd use pip install .)
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy pydantic pyyaml httpx

# Copy backend source
COPY backend/ ./backend/

# Copy built frontend assets to the shared dist folder
COPY --from=builder /app/frontend/dist /app/dist

# Expose port (Cloud Run defaults to 8080)
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["python3", "-m", "uvicorn", "backend.app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8080"]
