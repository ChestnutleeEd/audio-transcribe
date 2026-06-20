#!/usr/bin/env bash
set -euo pipefail

# ==================================================
# Audio-Transcribe macOS Stopper
# ==================================================
# Double-click this file on macOS to stop Audio-Transcribe.
# If macOS says the file cannot be opened, run:
#   chmod +x stop-audio-transcribe.command
# ==================================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_PORT="8000"
PID_FILE="$ROOT/data/tmp/audio-transcribe-server.pid"
STOPPED=0

echo "=================================================="
echo "Audio-Transcribe macOS Stopper"
echo "=================================================="
echo "This file is for macOS. Windows users should open:"
echo "  stop-audio-transcribe.bat"
echo

if [ -f "$PID_FILE" ]; then
  PID="$(tr -d '[:space:]' < "$PID_FILE")"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo "Stopping saved server process PID $PID..."
    kill "$PID" >/dev/null 2>&1 || true
    STOPPED=1
  else
    echo "Saved PID is not running: ${PID:-empty}"
  fi
  rm "$PID_FILE"
fi

echo
echo "Checking port $APP_PORT for remaining Audio-Transcribe server processes..."
PORT_PIDS="$(lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$PORT_PIDS" ]; then
  echo "Processes listening on port $APP_PORT:"
  printf "  %s\n" $PORT_PIDS
  for PID in $PORT_PIDS; do
    echo "Stopping PID $PID..."
    kill "$PID" >/dev/null 2>&1 || true
    STOPPED=1
  done
else
  echo "No process is listening on port $APP_PORT."
fi

echo
if [ "$STOPPED" -eq 1 ]; then
  echo "Stop command completed."
else
  echo "No running Audio-Transcribe server was found."
fi
echo
echo "If the page is still open in your browser, refresh it after stopping."
read -r -p "Press Return to close this window..."
