@echo off
setlocal

REM ==================================================
REM Audio-Transcribe Windows Launcher
REM ==================================================
REM Double-click this file on Windows to start Audio-Transcribe.
REM The launcher checks the local Python environment, installs missing
REM dependencies through scripts\setup-windows.ps1 when needed, starts the
REM FastAPI server, and opens the web UI in your default browser.
REM
REM To stop after startup:
REM   - Press Ctrl+C in this window, then type Y if Windows asks.
REM   - Or close this command window.
REM   - Or double-click stop-audio-transcribe.bat.
REM ==================================================

cd /d "%~dp0"
set "APP_URL=http://127.0.0.1:8000/"
set "APP_HOST=127.0.0.1"
set "APP_PORT=8000"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

echo ==================================================
echo Audio-Transcribe Windows Launcher
echo ==================================================
echo This file is for Windows. macOS users should open:
echo   start-audio-transcribe.command
echo.
echo Web UI:
echo   %APP_URL%
echo.

echo [1/4] Checking whether Audio-Transcribe is already running...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri '%APP_URL%' -TimeoutSec 2 > $null; exit 0 } catch { exit 1 }"
if "%ERRORLEVEL%"=="0" goto open_existing_app

echo [2/4] Checking Python virtual environment...
if not exist "%PYTHON_EXE%" (
  if exist "%CD%\scripts\setup-windows.ps1" (
    echo Python environment was not found. Running first-time setup...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\setup-windows.ps1"
  ) else (
    echo.
    echo Could not find:
    echo   %PYTHON_EXE%
    echo.
    echo Please install dependencies manually:
    echo   python -m venv .venv
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
  )
)

if not exist "%PYTHON_EXE%" (
  echo.
  echo Python environment is still missing after setup.
  echo Check whether Python is installed, then run scripts\setup-windows.ps1 again.
  echo.
  pause
  exit /b 1
)

echo [3/4] Starting backend on %APP_HOST%:%APP_PORT%...
echo.
echo If startup fails with "address already in use", port %APP_PORT% is occupied.
echo Close the other program or double-click stop-audio-transcribe.bat, then try again.
echo.
echo [4/4] Opening web UI after the server starts...
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process '%APP_URL%'" >nul 2>nul

echo ==================================================
echo Audio-Transcribe is starting.
echo Web UI: %APP_URL%
echo.
echo To stop:
echo   - Press Ctrl+C in this window, then type Y if Windows asks.
echo   - Or close this command window.
echo   - Or double-click stop-audio-transcribe.bat.
echo ==================================================
echo.

"%PYTHON_EXE%" -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%
goto done

:open_existing_app
echo Audio-Transcribe already appears to be running.
echo Opening the existing web UI:
echo   %APP_URL%
start "" "%APP_URL%"
echo.
echo To stop the existing service, double-click stop-audio-transcribe.bat.
echo.
pause

:done
endlocal
