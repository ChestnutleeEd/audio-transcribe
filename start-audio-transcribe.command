#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_URL="http://127.0.0.1:8000/"
PYTHON_EXE="$ROOT/.venv/bin/python"

if [ ! -x "$PYTHON_EXE" ]; then
  "$ROOT/scripts/setup-macos.sh"
fi

if curl --silent --fail --max-time 2 "$APP_URL" >/dev/null; then
  open "$APP_URL"
  exit 0
fi

"$PYTHON_EXE" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 >/tmp/audio-transcribe.log 2>&1 &
sleep 3
open "$APP_URL"
