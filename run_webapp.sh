#!/usr/bin/env bash
# Launch the HydroCare web app.
# Usage: ./run_webapp.sh   then open http://127.0.0.1:8000
set -e
cd "$(dirname "$0")"

PYTHON="${PYTHON:-.venv/bin/python}"
[ -x "$PYTHON" ] || PYTHON="python3"

echo "🌿 Starting HydroCare on http://127.0.0.1:8000 …"
exec "$PYTHON" -m uvicorn server:app --app-dir webapp --host 127.0.0.1 --port 8000 "$@"
