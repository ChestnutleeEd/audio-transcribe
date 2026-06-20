#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if ! command -v python3 >/dev/null 2>&1; then
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

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

".venv/bin/python" -m pip install --upgrade pip
".venv/bin/python" -m pip install --use-deprecated=legacy-resolver -r requirements.txt

echo "Audio Transcribe macOS 环境已准备完成。"
echo "启动命令：./start-audio-transcribe.command"
