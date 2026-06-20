$ErrorActionPreference = "Stop"

param(
  [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot ".."))
)

$Root = Resolve-Path $Root
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$RuntimePython = Join-Path $Root ".runtime\python\python.exe"
$Requirements = Join-Path $Root "requirements.txt"
$LocalFfmpeg = Join-Path $Root "origin-code\ffmpeg.exe"
$LocalFfprobe = Join-Path $Root "origin-code\ffprobe.exe"

Write-Host "正在检查 Audio-Transcribe 运行环境..."

if (-not (Test-Path $Requirements)) {
  Write-Host "未找到 requirements.txt。请确认当前目录是 Audio-Transcribe 根目录。"
  exit 1
}

if (Test-Path $RuntimePython) {
  $Python = $RuntimePython
}

if (-not (Test-Path $Python)) {
  Write-Host "未找到 Python 运行环境。"
  Write-Host "便携版首次运行会自动创建虚拟环境并安装依赖。"
  Write-Host "安装器版本应随包携带 Python runtime，若缺失请重新安装。"
  exit 2
}

$FfmpegCommand = Get-Command ffmpeg -ErrorAction SilentlyContinue
$FfprobeCommand = Get-Command ffprobe -ErrorAction SilentlyContinue
if ((-not $FfmpegCommand -or -not $FfprobeCommand) -and (-not (Test-Path $LocalFfmpeg) -or -not (Test-Path $LocalFfprobe))) {
  Write-Host "未检测到 FFmpeg / FFprobe。"
  Write-Host "请任选一种方式处理："
  Write-Host "  1. 安装 FFmpeg，并确保 ffmpeg 和 ffprobe 可以在命令行中直接运行。"
  Write-Host "  2. 把 ffmpeg.exe 和 ffprobe.exe 放到项目目录的 origin-code 文件夹。"
  Write-Host "FFmpeg 用于抽取音频、读取媒体时长和处理视频链接。"
  exit 3
}

try {
  & $Python -c "import fastapi, uvicorn, faster_whisper, yt_dlp" | Out-Null
} catch {
  Write-Host "Python 依赖尚未安装完整。"
  Write-Host "请运行："
  Write-Host "  .\scripts\setup-windows.ps1"
  exit 4
}

Write-Host "运行环境检查通过。"
exit 0
