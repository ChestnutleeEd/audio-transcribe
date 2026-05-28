@echo off
setlocal

cd /d "%~dp0"
set "APP_URL=http://localhost:8000/"
set "APP_HOST=127.0.0.1"
set "APP_PORT=8000"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri '%APP_URL%' -TimeoutSec 2 > $null; exit 0 } catch { exit 1 }"
if "%ERRORLEVEL%"=="0" goto open_app

if not exist "%PYTHON_EXE%" (
  echo Could not find .venv\Scripts\python.exe
  echo Please run:
  echo   python -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

start "Audio Transcribe Server" /min "%PYTHON_EXE%" -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%
timeout /t 3 /nobreak >nul

:open_app
start "" "%APP_URL%"
endlocal
