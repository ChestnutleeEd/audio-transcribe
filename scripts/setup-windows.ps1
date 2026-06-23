$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$RuntimePython = Join-Path $Root ".runtime\python\python.exe"

Set-Location $Root

if (Test-Path $RuntimePython) {
  Write-Host "已检测到安装器内置 Python runtime。"
  Write-Host "启动命令：.\start-audio-transcribe.bat"
  exit 0
}

if (-not (Test-Path $Python)) {
  $Launcher = Get-Command py -ErrorAction SilentlyContinue
  $SystemPython = Get-Command python -ErrorAction SilentlyContinue
  if ($Launcher) {
    py -3 -m venv .venv
  } elseif ($SystemPython) {
    python -m venv .venv
  } else {
    Write-Host "未检测到 Python。"
    Write-Host "请先安装 Python 3.10 或更新版本，然后重新运行："
    Write-Host "  .\start-audio-transcribe.bat"
    Write-Host "下载地址："
    Write-Host "  https://www.python.org/downloads/windows/"
    exit 1
  }
}

$PipIndexUrl = if ($env:PIP_INDEX_URL) { $env:PIP_INDEX_URL } else { "https://pypi.tuna.tsinghua.edu.cn/simple" }

& $Python -m pip install --upgrade pip
& $Python -m pip install -i $PipIndexUrl --use-deprecated=legacy-resolver -r requirements.txt

Write-Host "Audio Transcribe Windows 环境已准备完成。"
Write-Host "启动命令：.\start-audio-transcribe.bat"
