#!/usr/bin/env bash
set -euo pipefail

# ==================================================
# Audio-Transcribe macOS 停止器
# ==================================================
# macOS 用户双击此文件即可停止 Audio-Transcribe。
# 如果 macOS 提示无法打开，请运行：
#   chmod +x stop-audio-transcribe.command
# ==================================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

APP_PORT="8000"
PID_FILE="$ROOT/data/tmp/audio-transcribe-server.pid"
STOPPED=0

stop_pid() {
  local PID="$1"
  if [ -z "$PID" ] || ! kill -0 "$PID" >/dev/null 2>&1; then
    return 0
  fi

  echo "正在停止 PID $PID..."
  kill "$PID" >/dev/null 2>&1 || true
  for _ in {1..20}; do
    if ! kill -0 "$PID" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done

  if kill -0 "$PID" >/dev/null 2>&1; then
    echo "PID $PID 未响应普通停止信号，正在强制停止..."
    kill -9 "$PID" >/dev/null 2>&1 || true
  fi
}

echo "=================================================="
echo "Audio-Transcribe macOS 停止器"
echo "=================================================="
echo "此文件适用于 macOS。Windows 用户请打开："
echo "  stop-audio-transcribe.bat"
echo

if [ -f "$PID_FILE" ]; then
  PID="$(tr -d '[:space:]' < "$PID_FILE")"
  if [ -n "$PID" ] && kill -0 "$PID" >/dev/null 2>&1; then
    echo "发现 PID 文件记录的服务进程：$PID"
    stop_pid "$PID"
    STOPPED=1
  else
    echo "PID 文件记录的进程未运行：${PID:-空}"
  fi
  rm "$PID_FILE"
fi

echo
echo "正在检查端口 $APP_PORT 上是否仍有 Audio-Transcribe 服务进程..."
PORT_PIDS="$(lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN 2>/dev/null || true)"
if [ -n "$PORT_PIDS" ]; then
  echo "监听端口 $APP_PORT 的进程："
  printf "  %s\n" $PORT_PIDS
  for PID in $PORT_PIDS; do
    stop_pid "$PID"
    STOPPED=1
  done
else
  echo "端口 $APP_PORT 上没有监听进程。"
fi

echo
if [ "$STOPPED" -eq 1 ]; then
  REMAINING_PIDS="$(lsof -tiTCP:"$APP_PORT" -sTCP:LISTEN 2>/dev/null || true)"
  if [ -n "$REMAINING_PIDS" ]; then
    echo "停止命令已执行，但端口 $APP_PORT 仍被以下进程占用："
    printf "  %s\n" $REMAINING_PIDS
  else
    echo "停止命令已完成，端口 $APP_PORT 已释放。"
  fi
else
  echo "未找到正在运行的 Audio-Transcribe 服务。"
fi
echo
echo "如果浏览器页面仍然打开，请在停止后刷新页面。"
read -r -p "按回车键关闭此窗口..."
