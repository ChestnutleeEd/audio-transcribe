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
if [ -x "$ROOT/.runtime/python/bin/python3" ]; then
  PYTHON_EXE="$ROOT/.runtime/python/bin/python3"
fi
RUNTIME_DIR="$ROOT/data/tmp"
PID_FILE="$RUNTIME_DIR/audio-transcribe-server.pid"
SERVER_PID=""

export NO_PROXY="127.0.0.1,localhost,::1${NO_PROXY:+,$NO_PROXY}"
export no_proxy="127.0.0.1,localhost,::1${no_proxy:+,$no_proxy}"
if [ -x "$ROOT/origin-code/ffmpeg" ]; then
  export PATH="$ROOT/origin-code:$PATH"
  export AUDIO_TRANSCRIBE_FFMPEG="$ROOT/origin-code/ffmpeg"
fi

cleanup() {
  local PID="${SERVER_PID:-}"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo
    echo "正在停止 Audio-Transcribe 服务（PID $PID）..."
    kill "$PID" >/dev/null 2>&1 || true
    for _ in {1..20}; do
      if ! kill -0 "$PID" >/dev/null 2>&1; then
        break
      fi
      sleep 0.25
    done
    if kill -0 "$PID" >/dev/null 2>&1; then
      echo "服务未响应普通停止信号，正在强制停止..."
      kill -9 "$PID" >/dev/null 2>&1 || true
    fi
    wait "$PID" >/dev/null 2>&1 || true
  fi
  if [ -f "$PID_FILE" ]; then
    rm "$PID_FILE"
  fi
}

stop_existing_pid() {
  local PID="$1"
  if [ -z "$PID" ] || ! kill -0 "$PID" >/dev/null 2>&1; then
    return 0
  fi

  echo "发现已运行的 Audio-Transcribe 服务（PID $PID），正在重启以加载当前代码..."
  kill "$PID" >/dev/null 2>&1 || true
  for _ in {1..20}; do
    if ! kill -0 "$PID" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  if kill -0 "$PID" >/dev/null 2>&1; then
    echo "服务未响应普通停止信号，正在强制停止..."
    kill -9 "$PID" >/dev/null 2>&1 || true
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

echo "[1/5] 正在检查 Python 虚拟环境..."
if [ ! -x "$PYTHON_EXE" ]; then
  echo "未找到 Python 虚拟环境，正在执行首次安装..."
  if ! "$ROOT/scripts/setup-macos.sh"; then
    echo
    echo "首次安装未完成。请按照上方中文提示处理后重新双击启动。"
    read -r -p "按回车键关闭窗口。"
    exit 1
  fi
fi

echo "[2/5] 正在检查 Audio-Transcribe 是否已经运行..."
if [ -f "$PID_FILE" ]; then
  EXISTING_PID="$(tr -d '[:space:]' < "$PID_FILE")"
  stop_existing_pid "$EXISTING_PID"
  rm "$PID_FILE"
fi

if curl --noproxy "*" --silent --fail --max-time 2 "$APP_URL" >/dev/null; then
  echo "端口 $APP_PORT 已有服务响应，但不是当前启动器管理的进程。"
  echo "请先双击 stop-audio-transcribe.command 停止旧服务后再启动。"
  echo
  read -r -p "按回车键关闭窗口。"
  exit 1
fi

echo "[3/5] 正在检查 Python 依赖和 FFmpeg..."
if ! "$ROOT/scripts/runtime-check-macos.sh" "$ROOT"; then
  echo "检测到依赖不完整，正在使用国内镜像自动补齐..."
  if ! "$ROOT/scripts/setup-macos.sh" || ! "$ROOT/scripts/runtime-check-macos.sh" "$ROOT"; then
    echo
    echo "自动安装未完成。请按照上方中文提示处理后重新双击启动。"
    read -r -p "按回车键关闭窗口。"
    exit 1
  fi
fi

mkdir -p "$RUNTIME_DIR"

echo "[4/5] 正在启动后端服务：$APP_HOST:$APP_PORT..."
echo
echo "如果启动失败并提示 'address already in use'，说明端口 $APP_PORT 被占用。"
echo "请关闭占用端口的程序，或双击 stop-audio-transcribe.command 后重试。"
echo

"$PYTHON_EXE" -m uvicorn app.main:app --host "$APP_HOST" --port "$APP_PORT" &
SERVER_PID="$!"
printf "%s\n" "$SERVER_PID" > "$PID_FILE"

echo "[5/5] 正在打开网页..."
for _ in {1..30}; do
  if curl --noproxy "*" --silent --fail --max-time 1 "$APP_URL" >/dev/null; then
    break
  fi
  if ! kill -0 "$SERVER_PID" >/dev/null 2>&1; then
    echo
    echo "后端服务启动失败。请查看上方错误信息后重试。"
    read -r -p "按回车键关闭窗口。"
    exit 1
  fi
  sleep 1
done

if ! curl --noproxy "*" --silent --fail --max-time 2 "$APP_URL" >/dev/null; then
  echo
  echo "后端服务已启动，但网页暂时无法访问：$APP_URL"
  echo "请稍后手动刷新网页，或回到此窗口查看日志。"
fi
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
