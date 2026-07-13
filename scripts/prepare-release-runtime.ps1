param(
  [ValidateSet("windows", "macos")]
  [string]$Platform,
  [string]$PythonSeries = "3.12"
)

$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$PipIndexUrl = if ($env:PIP_INDEX_URL) { $env:PIP_INDEX_URL } else { "https://pypi.tuna.tsinghua.edu.cn/simple" }
$NpmRegistry = if ($env:NPM_CONFIG_REGISTRY) { $env:NPM_CONFIG_REGISTRY } else { "https://registry.npmmirror.com" }
$ReleaseTools = Join-Path $Root ".release-tools"
$OriginCode = Join-Path $Root "origin-code"

function Assert-EmptyTarget {
  param([string]$Path)
  if (Test-Path $Path) {
    throw "运行时目录已存在：$Path。为避免批量删除，请手动移走该目录后重试。"
  }
  New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Get-StandalonePythonAsset {
  param([string]$Pattern)

  $Headers = @{ "User-Agent" = "Audio-Transcribe release builder" }
  if ($env:GITHUB_TOKEN) {
    $Headers["Authorization"] = "Bearer $($env:GITHUB_TOKEN)"
  }
  $Release = Invoke-RestMethod -Headers $Headers -Uri "https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest"
  $Asset = $Release.assets | Where-Object { $_.name -match $Pattern } | Select-Object -First 1
  if (-not $Asset) {
    throw "未找到匹配的 Python standalone runtime：$Pattern"
  }
  return $Asset
}

function Install-PythonRuntime {
  param(
    [string]$Target,
    [string]$AssetPattern
  )

  Assert-EmptyTarget -Path $Target
  $Asset = Get-StandalonePythonAsset -Pattern $AssetPattern
  $Archive = Join-Path $ReleaseTools $Asset.name
  New-Item -ItemType Directory -Path $ReleaseTools -Force | Out-Null
  Write-Host "正在下载可再发行 Python：$($Asset.name)"
  Invoke-WebRequest -Uri $Asset.browser_download_url -OutFile $Archive
  & tar -xzf $Archive -C $Target
  if ($LASTEXITCODE -ne 0) {
    throw "Python runtime 解压失败。"
  }
}

function Install-StaticMediaTools {
  param([string]$TargetPlatform)

  New-Item -ItemType Directory -Path $OriginCode -Force | Out-Null
  New-Item -ItemType Directory -Path $ReleaseTools -Force | Out-Null
  & npm install --prefix $ReleaseTools --registry $NpmRegistry --no-audit --no-fund ffmpeg-static@5.3.0 ffprobe-static@3.1.0
  if ($LASTEXITCODE -ne 0) {
    Write-Warning "npmmirror 下载失败，正在回退到 npm 官方源。"
    & npm install --prefix $ReleaseTools --registry https://registry.npmjs.org --no-audit --no-fund ffmpeg-static@5.3.0 ffprobe-static@3.1.0
    if ($LASTEXITCODE -ne 0) {
      throw "FFmpeg 静态工具下载失败。"
    }
  }
  Push-Location $ReleaseTools
  try {
    $Ffmpeg = (& node -e "process.stdout.write(require('ffmpeg-static'))").Trim()
    $Ffprobe = (& node -e "process.stdout.write(require('ffprobe-static').path)").Trim()
  } finally {
    Pop-Location
  }
  if ($TargetPlatform -eq "windows") {
    Copy-Item $Ffmpeg (Join-Path $OriginCode "ffmpeg.exe")
    Copy-Item $Ffprobe (Join-Path $OriginCode "ffprobe.exe")
  } else {
    Copy-Item $Ffmpeg (Join-Path $OriginCode "ffmpeg")
    Copy-Item $Ffprobe (Join-Path $OriginCode "ffprobe")
    & chmod +x (Join-Path $OriginCode "ffmpeg") (Join-Path $OriginCode "ffprobe")
  }
}

if ($Platform -eq "windows") {
  $EscapedPythonSeries = [regex]::Escape($PythonSeries)
  $RuntimeRoot = Join-Path $Root "runtime/windows"
  Install-PythonRuntime -Target $RuntimeRoot -AssetPattern "^cpython-$EscapedPythonSeries\..*-x86_64-pc-windows-msvc-install_only\.tar\.gz$"
  $Python = Join-Path $RuntimeRoot "python/python.exe"
} else {
  $EscapedPythonSeries = [regex]::Escape($PythonSeries)
  $Architecture = (& uname -m).Trim()
  $PythonArchitecture = if ($Architecture -eq "arm64") { "aarch64" } else { "x86_64" }
  $RuntimeRoot = Join-Path $Root "runtime/macos"
  Install-PythonRuntime -Target $RuntimeRoot -AssetPattern "^cpython-$EscapedPythonSeries\..*-$PythonArchitecture-apple-darwin-install_only\.tar\.gz$"
  $Python = Join-Path $RuntimeRoot "python/bin/python3"
}

if (-not (Test-Path $Python -PathType Leaf)) {
  throw "Python runtime 主程序不存在：$Python"
}

Write-Host "正在通过清华 PyPI 镜像安装发行依赖..."
& $Python -m pip install --upgrade pip -i $PipIndexUrl
& $Python -m pip install -r (Join-Path $Root "requirements.txt") -i $PipIndexUrl --use-deprecated=legacy-resolver
if ($LASTEXITCODE -ne 0) {
  Write-Warning "清华 PyPI 镜像安装失败，正在回退到 PyPI 官方源。"
  & $Python -m pip install -r (Join-Path $Root "requirements.txt") -i https://pypi.org/simple --use-deprecated=legacy-resolver
  if ($LASTEXITCODE -ne 0) {
    throw "Python 依赖安装失败。"
  }
}

Install-StaticMediaTools -TargetPlatform $Platform
& $Python -c "import fastapi, uvicorn, faster_whisper, yt_dlp, docx; print('Python runtime verified')"
if ($LASTEXITCODE -ne 0) {
  throw "内置 Python runtime 验证失败。"
}

Write-Host "$Platform 可再发行运行环境准备完成。"
