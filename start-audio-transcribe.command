#!/usr/bin/env bash
set -euo pipefail

# ==================================================
# Audio-Transcribe macOS 启动器
# ==================================================
# macOS 用户双击此文件即可启动 Audio-Transcribe。
# 如果 macOS 提示无法打开，请运行：
#   chmod +x start-audio-transcribe.command
#
# 启动器会检查本地 Python 环境；必要时执行首次安装，启动 FastAPI 服务，
# 打开网页，并在此 Terminal 窗口退出时清理服务进程。
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
    echo "正在停止 Audio-Transcribe 服务（PID $SERVER_PID）..."
    kill "$SERVER_PID" >/dev/null 2>&1 || true
    wait "$SERVER_PID" >/dev/null 2>&1 || true
  fi
  if [ -f "$PID_FILE" ]; then
    rm "$PID_FILE"
  fi
}

trap cleanup EXIT INT TERM

echo "=================================================="
echo "Audio-Transcribe macOS 启动器"
echo "=================================================="
echo "此文件适用于 macOS。Windows 用户请打开："
echo "  start-audio-transcribe.bat"
echo
echo "网页地址："
echo "  $APP_URL"
echo

echo "[1/4] 正在检查 Python 虚拟环境..."
if [ ! -x "$PYTHON_EXE" ]; then
  echo "未找到 Python 虚拟环境，正在执行首次安装..."
  "$ROOT/scripts/setup-macos.sh"
fi

echo "[2/4] 正在检查 Audio-Transcribe 是否已经运行..."
if curl --silent --fail --max-time 2 "$APP_URL" >/dev/null; then
  echo "Audio-Transcribe 似乎已经在运行。"
  echo "正在打开现有网页："
  echo "  $APP_URL"
  open "$APP_URL"
  echo
  echo "如需停止现有服务，请双击 stop-audio-transcribe.command。"
  exit 0
fi

mkdir -p "$RUNTIME_DIR"

echo "[3/4] 正在启动后端服务：$APP_HOST:$APP_PORT..."
echo
echo "如果启动失败并提示 'address already in use'，说明端口 $APP_PORT 被占用。"
echo "请关闭占用端口的程序，或双击 stop-audio-transcribe.command 后重试。"
echo

"$PYTHON_EXE" -m uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT" &
SERVER_PID="$!"
printf "%s\n" "$SERVER_PID" > "$PID_FILE"

echo "[4/4] 正在打开网页..."
sleep 3
open "$APP_URL"

echo "=================================================="
echo "Audio-Transcribe 正在运行。"
echo "网页地址：$APP_URL"
echo
echo "关闭方式："
echo "  - 回到此 Terminal 窗口并按 Control+C。"
echo "  - 或直接关闭此 Terminal 窗口。"
echo "  - 或双击 stop-audio-transcribe.command。"
echo
echo "Apple Silicon 提示："
echo "  MLX Whisper 在 Apple Silicon 上可能更快，但此启动器不会自动"
echo "  安装 mlx-whisper，也不会自动下载模型。"
echo "=================================================="
echo

wait "$SERVER_PID"
