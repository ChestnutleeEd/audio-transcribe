#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
PYTHON_EXE="$ROOT/.venv/bin/python"
if [ -x "$ROOT/.runtime/python/bin/python3" ]; then
  PYTHON_EXE="$ROOT/.runtime/python/bin/python3"
fi
REQUIREMENTS="$ROOT/requirements.txt"

if [ -x "$ROOT/origin-code/ffmpeg" ]; then
  export PATH="$ROOT/origin-code:$PATH"
  export AUDIO_TRANSCRIBE_FFMPEG="$ROOT/origin-code/ffmpeg"
fi

echo "正在检查 Audio-Transcribe 运行环境..."

if [ ! -f "$REQUIREMENTS" ]; then
  echo "未找到 requirements.txt。请确认当前目录是 Audio-Transcribe 根目录。"
  exit 1
fi

if [ ! -x "$PYTHON_EXE" ]; then
  echo "未找到可用的 Python 运行环境：$PYTHON_EXE"
  echo "首次运行会自动准备运行环境并安装依赖。"
  exit 2
fi

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "未检测到 FFmpeg / FFprobe。"
  echo "请先安装 FFmpeg："
  echo "  brew install ffmpeg"
  echo "FFmpeg 用于抽取音频、读取媒体时长和处理视频链接。"
  exit 3
fi

if ! "$PYTHON_EXE" - <<'PY' >/dev/null 2>&1
import importlib.util
import platform

required = ["fastapi", "uvicorn", "faster_whisper", "yt_dlp"]
if platform.system().lower() == "darwin" and platform.machine().lower() in {"arm64", "aarch64"}:
    required.append("mlx_vlm")

missing = [name for name in required if importlib.util.find_spec(name) is None]
raise SystemExit(1 if missing else 0)
PY
then
  echo "Python 依赖尚未安装完整。"
  echo "请运行："
  echo "  ./scripts/setup-macos.sh"
  exit 4
fi

echo "运行环境检查通过。"
