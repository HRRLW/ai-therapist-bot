#!/usr/bin/env bash
set -euo pipefail

# Check python3 and pip
if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 not found. Please install Python 3.10+." >&2
  exit 1
fi
if ! command -v pip >/dev/null 2>&1 && ! command -v pip3 >/dev/null 2>&1; then
  echo "pip not found. Please install pip." >&2
  exit 1
fi

# Create venv
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# Activate venv
. .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Ensure .env exists
if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "Created .env from .env.example"
  else
    echo "Missing .env.example. Please provide environment variables." >&2
  fi
fi

# Load env
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs || true)
fi

# Echo current config
echo "Using OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://localhost:11434}"
echo "Using MODEL_NAME=${MODEL_NAME:-llama3:8b}"

# Start API
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
