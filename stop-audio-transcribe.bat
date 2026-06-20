@echo off
setlocal

REM ==================================================
REM Audio-Transcribe Windows Stopper
REM ==================================================
REM Double-click this file on Windows to stop Audio-Transcribe.
REM It first checks the saved PID file, then falls back to the server port.
REM ==================================================

cd /d "%~dp0"
set "APP_PORT=8000"
set "PID_FILE=%CD%\data\tmp\audio-transcribe-server.pid"
set "STOPPED=0"

echo ==================================================
echo Audio-Transcribe Windows Stopper
echo ==================================================
echo This file is for Windows. macOS users should open:
echo   stop-audio-transcribe.command
echo.

if exist "%PID_FILE%" (
  echo Checking PID file:
  echo   %PID_FILE%
  for /f "usebackq delims=" %%P in ("%PID_FILE%") do (
    if not "%%P"=="" (
      tasklist /FI "PID eq %%P" 2>nul | findstr /R /C:" %%P " >nul
      if not errorlevel 1 (
        echo Stopping saved server process PID %%P...
        taskkill /PID %%P /F
        set "STOPPED=1"
      ) else (
        echo Saved PID %%P is not running.
      )
    )
  )
)

echo.
echo Checking port %APP_PORT% for remaining Audio-Transcribe server processes...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%APP_PORT% .*LISTENING"') do (
  if not "%%P"=="0" (
    echo Stopping process listening on port %APP_PORT%: PID %%P
    taskkill /PID %%P /F
    set "STOPPED=1"
  )
)

echo.
if "%STOPPED%"=="1" (
  echo Stop command completed.
) else (
  echo No running Audio-Transcribe server was found on port %APP_PORT%.
)
echo.
echo If the page is still open in your browser, refresh it after stopping.
pause
endlocal
