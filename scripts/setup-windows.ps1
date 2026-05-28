$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $Root ".venv\Scripts\python.exe"

Set-Location $Root

if (-not (Test-Path $Python)) {
  $Launcher = Get-Command py -ErrorAction SilentlyContinue
  if ($Launcher) {
    py -3 -m venv .venv
  } else {
    python -m venv .venv
  }
}

& $Python -m pip install --upgrade pip
& $Python -m pip install --use-deprecated=legacy-resolver -r requirements.txt

Write-Host "Audio Transcribe Windows environment is ready."
Write-Host "Start with: .\start-audio-transcribe.bat"
