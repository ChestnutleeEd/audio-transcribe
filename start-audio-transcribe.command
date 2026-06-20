#!/usr/bin/env bash
set -euo pipefail

# ==================================================
# Audio-Transcribe macOS Launcher
# ==================================================
# Double-click this file on macOS to start Audio-Transcribe.
# If macOS says the file cannot be opened, run:
#   chmod +x start-audio-transcribe.command
#
# The launcher checks the local Python environment, runs first-time setup
# when needed, starts the FastAPI server, opens the web UI, and cleans up
# the server process when this Terminal window exits.
# ==================================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_URL="http://127.0.0.1:8000/"
APP_HOST="127.0.0.1"
APP_PORT="8000"
PYTHON_EXE="$ROOT/.venv/bin/python"
RUNTIME_DIR="$ROOT/data/tmp"
PID_FILE="$RUNTIME_DIR/audio-transcribe-server.pid"
SERVER_PID=""

cleanup() {
  if [ -n "${SERVER_PID:-}" ] && kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo
    echo "Stopping Audio-Transcribe server (PID $SERVER_PID)..."
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  if [ -f "$PID_FILE" ]; then
    rm "$PID_FILE"
  fi
}

trap cleanup EXIT INT TERM

echo "=================================================="
echo "Audio-Transcribe macOS Launcher"
echo "=================================================="
echo "This file is for macOS. Windows users should open:"
echo "  start-audio-transcribe.bat"
echo
echo "Web UI:"
echo "  $APP_URL"
echo

echo "[1/4] Checking Python virtual environment..."
if [ ! -x "$PYTHON_EXE" ]; then
  echo "Python environment was not found. Running first-time setup..."
  "$ROOT/scripts/setup-macos.sh"
fi

echo "[2/4] Checking whether Audio-Transcribe is already running..."
if curl --silent --fail --max-time 2 "$APP_URL" >/dev/null; then
  echo "Audio-Transcribe already appears to be running."
  echo "Opening the existing web UI:"
  echo "  $APP_URL"
  open "$APP_URL"
  echo
  echo "To stop the existing service, double-click stop-audio-transcribe.command."
  exit 0
fi

mkdir -p "$RUNTIME_DIR"

echo "[3/4] Starting backend on $APP_HOST:$APP_PORT..."
echo
echo "If startup fails with 'address already in use', port $APP_PORT is occupied."
echo "Close the other program or double-click stop-audio-transcribe.command, then try again."
echo

"$PYTHON_EXE" -m uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT" &
SERVER_PID="$!"
printf "%s\n" "$SERVER_PID" > "$PID_FILE"

echo "[4/4] Opening web UI..."
sleep 3
open "$APP_URL"

echo "=================================================="
echo "Audio-Transcribe is running."
echo "Web UI: $APP_URL"
echo
echo "To stop:"
echo "  - Return to this Terminal window and press Control+C."
echo "  - Or close this Terminal window."
echo "  - Or double-click stop-audio-transcribe.command."
echo
echo "Apple Silicon note:"
echo "  MLX Whisper can be faster on Apple Silicon, but this launcher will not"
echo "  install mlx-whisper or download models automatically."
echo "=================================================="
echo

wait "$SERVER_PID"
