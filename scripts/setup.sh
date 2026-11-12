#!/usr/bin/env bash

set -euo pipefail

# Resolve the project root independently of the caller's working directory.
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
cd -- "$PROJECT_DIR"

if [[ $# -gt 1 || ( $# -eq 1 && "$1" != "--no-start" ) ]]; then
  printf 'Usage: bash scripts/setup.sh [--no-start]\n' >&2
  exit 1
fi

# Linux/macOS/WSL usually expose python3; Git Bash may only expose python.
if command -v python3 >/dev/null 2>&1 && python3 -c 'import sys' >/dev/null 2>&1; then
  PYTHON_COMMAND=python3
elif command -v python >/dev/null 2>&1 && python -c 'import sys' >/dev/null 2>&1; then
  PYTHON_COMMAND=python
else
  printf 'ERROR: Python is not installed or is not available in PATH.\n' >&2
  exit 1
fi

printf 'Preparing the development environment...\n'
if [[ ! -d .venv ]]; then
  "$PYTHON_COMMAND" -m venv .venv
fi

# Invoke the environment's interpreter directly; activation is not needed.
if [[ -x .venv/bin/python ]]; then
  VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"
elif [[ -f .venv/Scripts/python.exe ]]; then
  VENV_PYTHON="$PROJECT_DIR/.venv/Scripts/python.exe"
else
  printf 'ERROR: .venv has no usable Python interpreter. Check or recreate it manually.\n' >&2
  exit 1
fi

"$VENV_PYTHON" -m pip install --upgrade pip
"$VENV_PYTHON" -m pip install -r requirements.txt

printf 'Environment setup completed.\n'
if [[ "${1:-}" == "--no-start" ]]; then
  exit 0
fi

printf 'Starting the FastAPI development server...\n'
# Load dotenv before app imports without executing .env as shell code.
exec "$VENV_PYTHON" -c 'from dotenv import load_dotenv; load_dotenv(".env"); import uvicorn; uvicorn.run("app.main:app", reload=True)'
