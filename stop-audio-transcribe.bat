@echo off
setlocal

REM ==================================================
REM Audio-Transcribe Windows 停止器
REM ==================================================
REM Windows 用户双击此文件即可停止 Audio-Transcribe。
REM 脚本会先检查保存的 PID 文件，再按服务端口兜底查找。
REM ==================================================

cd /d "%~dp0"
set "APP_PORT=8000"
set "PID_FILE=%CD%\data\tmp\audio-transcribe-server.pid"
set "STOPPED=0"

echo ==================================================
echo Audio-Transcribe Windows 停止器
echo ==================================================
echo 此文件适用于 Windows。macOS 用户请打开：
echo   stop-audio-transcribe.command
echo.

if exist "%PID_FILE%" (
  echo 正在检查 PID 文件：
  echo   %PID_FILE%
  for /f "usebackq delims=" %%P in ("%PID_FILE%") do (
    if not "%%P"=="" (
      tasklist /FI "PID eq %%P" 2>nul | findstr /R /C:" %%P " >nul
      if not errorlevel 1 (
        echo 正在停止 PID 文件记录的服务进程：%%P...
        taskkill /PID %%P /F
        set "STOPPED=1"
      ) else (
        echo PID 文件记录的进程 %%P 未运行。
      )
    )
  )
)

echo.
echo 正在检查端口 %APP_PORT% 上是否仍有 Audio-Transcribe 服务进程...
for /f "tokens=5" %%P in ('netstat -ano ^| findstr /R /C:":%APP_PORT% .*LISTENING"') do (
  if not "%%P"=="0" (
    echo 正在停止监听端口 %APP_PORT% 的进程：PID %%P
    taskkill /PID %%P /F
    set "STOPPED=1"
  )
)

echo.
if "%STOPPED%"=="1" (
  echo 停止命令已完成。
) else (
  echo 未在端口 %APP_PORT% 上找到正在运行的 Audio-Transcribe 服务。
)
echo.
echo 如果浏览器页面仍然打开，请在停止后刷新页面。
pause
endlocal
