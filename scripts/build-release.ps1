param(
  [string]$Version = "v0.1.0"
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Dist = Join-Path $Root "release-dist\$Version"
$WindowsStage = Join-Path $Dist "AudioTranscribe-$Version-windows-x64"
$MacStage = Join-Path $Dist "AudioTranscribe-$Version-macos"

function Copy-ReleaseTree {
  param(
    [string]$Source,
    [string]$Destination
  )

  New-Item -ItemType Directory -Path $Destination -Force | Out-Null
  $SourcePath = Resolve-Path $Source
  Get-ChildItem -Path $SourcePath -Recurse -File |
    Where-Object {
      $_.FullName -notmatch "\\__pycache__\\" -and
      $_.Name -notlike "*.pyc"
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

if (Test-Path $Dist) {
  throw "Release directory already exists: $Dist. Move it aside manually before rebuilding."
}

New-Item -ItemType Directory -Path $WindowsStage | Out-Null
New-Item -ItemType Directory -Path $MacStage | Out-Null

$CommonItems = @(
  "app",
  "static",
  "docs",
  "scripts",
  "README.md",
  "requirements.txt",
  ".gitignore"
)

foreach ($Item in $CommonItems) {
  $Source = Join-Path $Root $Item
  $WindowsTarget = Join-Path $WindowsStage $Item
  $MacTarget = Join-Path $MacStage $Item
  if (Test-Path $Source -PathType Container) {
    Copy-ReleaseTree -Source $Source -Destination $WindowsTarget
    Copy-ReleaseTree -Source $Source -Destination $MacTarget
  } else {
    Copy-Item -Path $Source -Destination $WindowsTarget
    Copy-Item -Path $Source -Destination $MacTarget
  }
}

Copy-Item -Path (Join-Path $Root "start-audio-transcribe.bat") -Destination $WindowsStage
Copy-Item -Path (Join-Path $Root "start-audio-transcribe.command") -Destination $MacStage

if (Test-Path (Join-Path $Root ".venv")) {
  Copy-Item -Path (Join-Path $Root ".venv") -Destination (Join-Path $WindowsStage ".venv") -Recurse
}

$OriginCodeStage = Join-Path $WindowsStage "origin-code"
New-Item -ItemType Directory -Path $OriginCodeStage | Out-Null
foreach ($Tool in @("ffmpeg.exe", "ffprobe.exe")) {
  $ToolPath = Join-Path $Root "origin-code\$Tool"
  if (Test-Path $ToolPath) {
    Copy-Item -Path $ToolPath -Destination $OriginCodeStage
  }
}

Compress-Archive -Path $WindowsStage -DestinationPath (Join-Path $Dist "AudioTranscribe-$Version-windows-x64.zip")
Compress-Archive -Path $MacStage -DestinationPath (Join-Path $Dist "AudioTranscribe-$Version-macos.zip")

Write-Host "Release assets created in $Dist"
