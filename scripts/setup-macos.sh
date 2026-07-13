#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PIP_INDEX_URL="${PIP_INDEX_URL:-https://pypi.tuna.tsinghua.edu.cn/simple}"
PYTHON_EXE="$ROOT/.venv/bin/python"

if [ -x "$ROOT/.runtime/python/bin/python3" ]; then
  PYTHON_EXE="$ROOT/.runtime/python/bin/python3"
fi

if [ -x "$ROOT/origin-code/ffmpeg" ]; then
  export PATH="$ROOT/origin-code:$PATH"
  export AUDIO_TRANSCRIBE_FFMPEG="$ROOT/origin-code/ffmpeg"
fi

if [ ! -x "$PYTHON_EXE" ] && ! command -v python3 >/dev/null 2>&1; then
  echo "未检测到 Python 3。"
  echo "请先安装 Python 3.10 或更新版本，然后重新运行："
  echo "  ./start-audio-transcribe.command"
  echo "推荐命令："
  echo "  brew install python"
  exit 1
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "需要安装 ffmpeg，用于音视频预处理。"
  echo "推荐命令：brew install ffmpeg"
  exit 1
fi

if [ ! -x "$PYTHON_EXE" ]; then
  python3 -m venv .venv
  PYTHON_EXE="$ROOT/.venv/bin/python"
fi

"$PYTHON_EXE" -m pip install --upgrade pip -i "$PIP_INDEX_URL"
"$PYTHON_EXE" -m pip install -i "$PIP_INDEX_URL" --use-deprecated=legacy-resolver -r requirements.txt

echo "Audio Transcribe macOS 环境已准备完成。"
echo "启动命令：./start-audio-transcribe.command"
