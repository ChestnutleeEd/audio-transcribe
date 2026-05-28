#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required. Install it from https://www.python.org/downloads/ or Homebrew."
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg is required for media preprocessing."
  echo "Recommended: brew install ffmpeg"
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install --use-deprecated=legacy-resolver -r requirements.txt

echo "Audio Transcribe macOS environment is ready."
echo "Start with: ./start-audio-transcribe.command"
