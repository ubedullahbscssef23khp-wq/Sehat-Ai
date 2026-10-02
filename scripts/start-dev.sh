#!/bin/bash
set -e

# 1. Ensure frontend dependencies are installed
if [ ! -f "frontend/node_modules/.bin/vite" ]; then
  echo "Installing frontend dependencies..."
  npm --prefix frontend install
fi

# 2. Ensure python venv exists for backend
if [ ! -f "backend/.venv/bin/uvicorn" ]; then
  echo "Setting up backend virtual environment..."
  if ! which virtualenv >/dev/null 2>&1; then
    if ! which pip >/dev/null 2>&1 && ! which pip3 >/dev/null 2>&1; then
      if [ -f "get-pip.py" ]; then
        python3 get-pip.py --user
      else
        curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
        python3 get-pip.py --user
      fi
    fi
    /root/.local/bin/pip install virtualenv || pip install virtualenv || true
  fi
  python3 -m virtualenv backend/.venv
  backend/.venv/bin/pip install -e "backend/.[dev]"
fi

# 3. Start backend and frontend concurrently
npx concurrently \
  "cd backend && SEHAT_LLM_PROVIDER=dashscope DASHSCOPE_API_KEY=$GEMINI_API_KEY DASHSCOPE_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai SEHAT_LLM_MODEL=gemini-3.6-flash .venv/bin/python3 -m uvicorn app.main:create_app --factory --port 8001" \
  "npm --prefix frontend run dev"
