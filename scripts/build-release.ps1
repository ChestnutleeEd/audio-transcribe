param(
  [string]$Version = "v0.4.0",
  [ValidateSet("all", "zip", "zip-windows", "zip-macos", "installer", "installer-windows", "installer-macos")]
  [string]$Target = "all"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$DistRoot = Join-Path $Root "dist"
$ZipRoot = Join-Path $DistRoot "zip"
$InstallerRoot = Join-Path $DistRoot "installer"
$WindowsZipRoot = Join-Path $ZipRoot "windows"
$MacZipRoot = Join-Path $ZipRoot "macos"
$WindowsInstallerRoot = Join-Path $InstallerRoot "windows"
$MacInstallerRoot = Join-Path $InstallerRoot "macos"

function Write-ReleaseWarning {
  param([string]$Message)
  Write-Host "警告：$Message" -ForegroundColor Yellow
}

function Assert-NewDirectory {
  param([string]$Path)

  if (Test-Path $Path) {
    throw "发行目录已存在：$Path。为避免误删文件，请手动移走或删除该明确目录后重新构建。"
  }
  New-Item -ItemType Directory -Path $Path -Force | Out-Null
}

function Test-ZipArtifact {
  param([string]$Path)

  return (Test-Path $Path -PathType Leaf) -and ((Get-Item $Path).Length -gt 0)
}

function Ensure-WindowsZipFallback {
  $OutputDir = Join-Path $WindowsZipRoot $Version
  $ZipPath = Join-Path $OutputDir "AudioTranscribe-$Version-windows-x64.zip"
  if (Test-ZipArtifact -Path $ZipPath) {
    Write-Host "Windows ZIP fallback 已存在：$ZipPath"
    return
  }
  Write-Host "正在生成 Windows ZIP fallback..."
  build_zip_windows
}

function Ensure-MacZipFallback {
  $OutputDir = Join-Path $MacZipRoot $Version
  $ZipPath = Join-Path $OutputDir "AudioTranscribe-$Version-macos.zip"
  if (Test-ZipArtifact -Path $ZipPath) {
    Write-Host "macOS ZIP fallback 已存在：$ZipPath"
    return
  }
  Write-Host "正在生成 macOS ZIP fallback..."
  build_zip_macos
}

function Get-InnoSetupCompiler {
  $Command = Get-Command ISCC.exe -ErrorAction SilentlyContinue
  if ($Command) {
    return $Command.Source
  }
  $CandidatePaths = @(
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles}\Inno Setup 6\ISCC.exe"
  )
  foreach ($Candidate in $CandidatePaths) {
    if ($Candidate -and (Test-Path $Candidate -PathType Leaf)) {
      return $Candidate
    }
  }
  return $null
}

function Copy-ReleaseTree {
  param(
    [string]$Source,
    [string]$Destination
  )

  New-Item -ItemType Directory -Path $Destination -Force | Out-Null
  $SourcePath = Resolve-Path $Source
  Get-ChildItem -Path $SourcePath -Recurse -File |
    Where-Object {
      $_.FullName -notmatch "[\\/]\.venv[\\/]" -and
      $_.FullName -notmatch "[\\/]__pycache__[\\/]" -and
      $_.FullName -notmatch "[\\/]data[\\/](uploads|jobs|tmp)[\\/]" -and
      $_.Name -notlike "*.pyc" -and
      $_.Name -ne ".DS_Store"
    } |
    ForEach-Object {
      $Relative = $_.FullName.Substring($SourcePath.Path.Length).TrimStart("\", "/")
      $Target = Join-Path $Destination $Relative
      $TargetDir = Split-Path $Target -Parent
      if (-not (Test-Path $TargetDir)) {
        New-Item -ItemType Directory -Path $TargetDir | Out-Null
      }
      Copy-Item -Path $_.FullName -Destination $Target
    }
}

function Copy-CommonApplication {
  param([string]$Stage)

  $CommonItems = @(
    "app",
    "static",
    "docs",
    "scripts",
    "packaging",
    "README.md",
    "requirements.txt",
    "requirements-qwen-audio.txt",
    ".gitignore"
  )

  foreach ($Item in $CommonItems) {
    $Source = Join-Path $Root $Item
    $Target = Join-Path $Stage $Item
    if (Test-Path $Source -PathType Container) {
      Copy-ReleaseTree -Source $Source -Destination $Target
    } elseif (Test-Path $Source) {
      Copy-Item -Path $Source -Destination $Target
    }
  }

  $ConfigDir = Join-Path $Stage "config"
  New-Item -ItemType Directory -Path $ConfigDir -Force | Out-Null
  @(
    "# Audio-Transcribe 默认配置",
    "# 安装器和便携版都会携带此文件，用户可按需复制为 .env 后修改。",
    "AUDIO_TRANSCRIBE_DEVICE=auto",
    "AUDIO_TRANSCRIBE_COMPUTE_TYPE=auto",
    "OLLAMA_BASE_URL=http://localhost:11434"
  ) | Set-Content -Path (Join-Path $ConfigDir "audio-transcribe.defaults.env") -Encoding UTF8
}

function Copy-WindowsRuntimeIfAvailable {
  param([string]$Stage)

  $RuntimeStage = Join-Path $Stage ".runtime\python"
  $EmbeddedPython = Join-Path $Root "runtime\windows\python"
  $WindowsVenv = Join-Path $Root ".venv"

  if (Test-Path (Join-Path $EmbeddedPython "python.exe")) {
    Copy-ReleaseTree -Source $EmbeddedPython -Destination $RuntimeStage
    Write-Host "已复制 Windows Python runtime：$RuntimeStage"
  } elseif ((Test-Path $WindowsVenv) -and (Test-Path (Join-Path $WindowsVenv "Scripts\python.exe"))) {
    Copy-Item -Path $WindowsVenv -Destination (Join-Path $Stage ".venv") -Recurse
    Write-Host "已复制 Windows 虚拟环境：$WindowsVenv"
  } else {
    Write-Host "未找到 Windows Python runtime。Windows 包会在首次启动时引导用户安装 Python 依赖。"
  }

  $OriginCodeStage = Join-Path $Stage "origin-code"
  New-Item -ItemType Directory -Path $OriginCodeStage -Force | Out-Null
  $OriginCode = Join-Path $Root "origin-code"
  foreach ($Tool in @("ffmpeg.exe", "ffprobe.exe")) {
    $ToolPath = Join-Path $OriginCode $Tool
    if (Test-Path $ToolPath) {
      Copy-Item -Path $ToolPath -Destination $OriginCodeStage
    }
  }
}

function Copy-MacRuntimeIfAvailable {
  param([string]$Stage)

  $EmbeddedPython = Join-Path $Root "runtime/macos/python"
  $MacVenv = Join-Path $Root ".venv"
  if (Test-Path (Join-Path $EmbeddedPython "bin/python3")) {
    Copy-ReleaseTree -Source $EmbeddedPython -Destination (Join-Path $Stage ".runtime/python")
    Write-Host "已复制 macOS Python runtime：$EmbeddedPython"
  } elseif ((Test-Path $MacVenv) -and (Test-Path (Join-Path $MacVenv "bin/python"))) {
    Copy-Item -Path $MacVenv -Destination (Join-Path $Stage ".venv") -Recurse
    Write-Host "已复制 macOS 虚拟环境：$MacVenv"
  } else {
    Write-Host "未找到 macOS 虚拟环境。macOS 包会在首次启动时引导用户安装 Python 依赖。"
  }

  $OriginCodeStage = Join-Path $Stage "origin-code"
  New-Item -ItemType Directory -Path $OriginCodeStage -Force | Out-Null
  $OriginCode = Join-Path $Root "origin-code"
  foreach ($Tool in @("ffmpeg", "ffprobe")) {
    $ToolPath = Join-Path $OriginCode $Tool
    if (Test-Path $ToolPath) {
      Copy-Item -Path $ToolPath -Destination $OriginCodeStage
      & chmod +x (Join-Path $OriginCodeStage $Tool)
    }
  }
}

function New-WindowsStage {
  param([string]$Stage)

  Assert-NewDirectory -Path $Stage
  Copy-CommonApplication -Stage $Stage
  Copy-Item -Path (Join-Path $Root "start-audio-transcribe.bat") -Destination $Stage
  Copy-Item -Path (Join-Path $Root "stop-audio-transcribe.bat") -Destination $Stage
  Copy-WindowsRuntimeIfAvailable -Stage $Stage
}

function New-MacStage {
  param([string]$Stage)

  Assert-NewDirectory -Path $Stage
  Copy-CommonApplication -Stage $Stage
  Copy-Item -Path (Join-Path $Root "start-audio-transcribe.command") -Destination $Stage
  Copy-Item -Path (Join-Path $Root "stop-audio-transcribe.command") -Destination $Stage
  Copy-MacRuntimeIfAvailable -Stage $Stage
}

function build_zip_windows {
  $OutputDir = Join-Path $WindowsZipRoot $Version
  $Stage = Join-Path $OutputDir "AudioTranscribe-$Version-windows-x64"
  Assert-NewDirectory -Path $OutputDir
  New-WindowsStage -Stage $Stage
  $ZipPath = Join-Path $OutputDir "AudioTranscribe-$Version-windows-x64.zip"
  Compress-Archive -Path $Stage -DestinationPath $ZipPath
  Write-Host "Windows ZIP 已创建：$ZipPath"
}

function build_zip_macos {
  $OutputDir = Join-Path $MacZipRoot $Version
  $Stage = Join-Path $OutputDir "AudioTranscribe-$Version-macos"
  Assert-NewDirectory -Path $OutputDir
  New-MacStage -Stage $Stage
  $ZipPath = Join-Path $OutputDir "AudioTranscribe-$Version-macos.zip"
  if ($IsMacOS) {
    & ditto -c -k --sequesterRsrc --keepParent $Stage $ZipPath
  } else {
    Compress-Archive -Path $Stage -DestinationPath $ZipPath
  }
  Write-Host "macOS ZIP 已创建：$ZipPath"
}

function build_installer_windows {
  $Iscc = Get-InnoSetupCompiler
  if (-not $Iscc) {
    Write-ReleaseWarning "未检测到 Inno Setup 编译器 ISCC.exe。Windows Installer 已跳过，不会生成假安装包。"
    Write-Host "请在 Windows 构建机安装 Inno Setup 后重新运行：.\scripts\build-release.ps1 -Version $Version -Target installer-windows"
    Ensure-WindowsZipFallback
    return
  }

  $OutputDir = Join-Path $WindowsInstallerRoot $Version
  $Stage = Join-Path $OutputDir "stage\AudioTranscribe"
  Assert-NewDirectory -Path $OutputDir
  New-WindowsStage -Stage $Stage

  $env:AUDIO_TRANSCRIBE_VERSION = $Version.TrimStart("v")
  $env:AUDIO_TRANSCRIBE_WINDOWS_STAGE = $Stage
  $env:AUDIO_TRANSCRIBE_WINDOWS_INSTALLER_DIR = $OutputDir
  & $Iscc (Join-Path $Root "packaging\windows\AudioTranscribe.iss")
  if ($LASTEXITCODE -ne 0) {
    Write-ReleaseWarning "Inno Setup 构建失败，已跳过 Windows Installer。"
    Ensure-WindowsZipFallback
    return
  }
  $SetupPath = Join-Path $OutputDir "AudioTranscribeSetup.exe"
  if (-not (Test-Path $SetupPath -PathType Leaf) -or ((Get-Item $SetupPath).Length -le 0)) {
    Write-ReleaseWarning "Inno Setup 未生成真实 AudioTranscribeSetup.exe，已跳过 Windows Installer。"
    Ensure-WindowsZipFallback
    return
  }
  Write-Host "Windows Installer 已创建：$SetupPath"
}

function build_installer_macos {
  if ($IsWindows -or (-not $IsMacOS)) {
    Write-ReleaseWarning "macOS Installer 只能在 macOS 构建机生成。已跳过 dmg/app bundle，不会生成假安装包。"
    Ensure-MacZipFallback
    return
  }

  $OutputDir = Join-Path $MacInstallerRoot $Version
  $DmgStage = Join-Path $OutputDir "dmg-stage"
  $AppRoot = Join-Path $DmgStage "Audio-Transcribe.app"
  $Contents = Join-Path $AppRoot "Contents"
  $MacOS = Join-Path $Contents "MacOS"
  $Resources = Join-Path $Contents "Resources"
  $AppResources = Join-Path $Resources "audio-transcribe"
  Assert-NewDirectory -Path $OutputDir

  New-Item -ItemType Directory -Path $MacOS -Force | Out-Null
  New-Item -ItemType Directory -Path $Resources -Force | Out-Null
  Copy-Item -Path (Join-Path $Root "packaging\macos\Info.plist") -Destination (Join-Path $Contents "Info.plist")
  $InfoPath = Join-Path $Contents "Info.plist"
  $CleanVersion = $Version.TrimStart("v")
  (Get-Content -Path $InfoPath -Raw) -replace "<string>1\.0\.0</string>", "<string>$CleanVersion</string>" |
    Set-Content -Path $InfoPath -Encoding UTF8
  Copy-Item -Path (Join-Path $Root "packaging\macos\AudioTranscribe") -Destination (Join-Path $MacOS "AudioTranscribe")
  New-MacStage -Stage $AppResources

  & chmod +x (Join-Path $MacOS "AudioTranscribe")
  & chmod +x (Join-Path $AppResources "start-audio-transcribe.command")
  & chmod +x (Join-Path $AppResources "stop-audio-transcribe.command")

  $DmgPath = Join-Path $OutputDir "AudioTranscribe.dmg"
  $CreateDmg = Get-Command create-dmg -ErrorAction SilentlyContinue
  if ($CreateDmg) {
    & $CreateDmg.Source `
      --volname "Audio-Transcribe" `
      --app-drop-link 420 180 `
      $DmgPath `
      $DmgStage
    if ($LASTEXITCODE -eq 0 -and (Test-Path $DmgPath -PathType Leaf) -and ((Get-Item $DmgPath).Length -gt 0)) {
      Write-Host "macOS dmg 已创建：$DmgPath"
      return
    }
    Write-ReleaseWarning "create-dmg 构建失败，正在 fallback 为 .app bundle ZIP。"
  } else {
    Write-ReleaseWarning "未检测到 create-dmg，正在 fallback 为 .app bundle ZIP。"
  }

  $AppZipPath = Join-Path $OutputDir "AudioTranscribeAppBundle.zip"
  if ($IsMacOS) {
    & ditto -c -k --sequesterRsrc --keepParent $AppRoot $AppZipPath
  } else {
    Compress-Archive -Path $AppRoot -DestinationPath $AppZipPath
  }
  if (-not (Test-ZipArtifact -Path $AppZipPath)) {
    Write-ReleaseWarning "macOS .app bundle ZIP 生成失败。"
    Ensure-MacZipFallback
    return
  }
  Write-Host "macOS .app bundle ZIP 已创建：$AppZipPath"
}

switch ($Target) {
  "all" {
    build_zip_windows
    build_zip_macos
    build_installer_windows
    build_installer_macos
  }
  "zip" {
    build_zip_windows
    build_zip_macos
  }
  "zip-windows" { build_zip_windows }
  "zip-macos" { build_zip_macos }
  "installer" {
    build_installer_windows
    build_installer_macos
  }
  "installer-windows" { build_installer_windows }
  "installer-macos" { build_installer_macos }
}
