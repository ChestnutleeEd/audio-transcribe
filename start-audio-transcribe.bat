@echo off
setlocal

REM ==================================================
REM Audio-Transcribe Windows 启动器
REM ==================================================
REM Windows 用户双击此文件即可启动 Audio-Transcribe。
REM 启动器会检查本地 Python 环境；必要时通过 scripts\setup-windows.ps1
REM 安装缺失依赖，然后启动 FastAPI 服务，并在默认浏览器中打开网页。
REM
REM 启动后如需关闭：
REM   - 在此窗口按 Ctrl+C；如果 Windows 询问是否终止，请输入 Y。
REM   - 或直接关闭此命令行窗口。
REM   - 或双击 stop-audio-transcribe.bat。
REM ==================================================

cd /d "%~dp0"
set "APP_URL=http://127.0.0.1:8000/"
set "APP_HOST=127.0.0.1"
set "APP_PORT=8000"
set "PYTHON_EXE=%CD%\.venv\Scripts\python.exe"

echo ==================================================
echo Audio-Transcribe Windows 启动器
echo ==================================================
echo 此文件适用于 Windows。macOS 用户请打开：
echo   start-audio-transcribe.command
echo.
echo 网页地址：
echo   %APP_URL%
echo.

echo [1/4] 正在检查 Audio-Transcribe 是否已经运行...
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { Invoke-WebRequest -UseBasicParsing -Uri '%APP_URL%' -TimeoutSec 2 > $null; exit 0 } catch { exit 1 }"
if "%ERRORLEVEL%"=="0" goto open_existing_app

echo [2/4] 正在检查 Python 虚拟环境...
if not exist "%PYTHON_EXE%" (
  if exist "%CD%\scripts\setup-windows.ps1" (
    echo 未找到 Python 虚拟环境，正在执行首次安装...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%CD%\scripts\setup-windows.ps1"
  ) else (
    echo.
    echo 找不到：
    echo   %PYTHON_EXE%
    echo.
    echo 请手动安装依赖：
    echo   python -m venv .venv
    echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
    echo.
    pause
    exit /b 1
  )
)

if not exist "%PYTHON_EXE%" (
  echo.
  echo 安装后仍未找到 Python 虚拟环境。
  echo 请确认 Python 已安装，然后重新运行 scripts\setup-windows.ps1。
  echo.
  pause
  exit /b 1
)

echo [3/4] 正在启动后端服务：%APP_HOST%:%APP_PORT%...
echo.
echo 如果启动失败并提示 "address already in use"，说明端口 %APP_PORT% 被占用。
echo 请关闭占用端口的程序，或双击 stop-audio-transcribe.bat 后重试。
echo.
echo [4/4] 服务启动后将自动打开网页...
powershell -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process '%APP_URL%'" >nul 2>nul

echo ==================================================
echo Audio-Transcribe 正在启动。
echo 网页地址：%APP_URL%
echo.
echo 关闭方式：
echo   - 在此窗口按 Ctrl+C；如果 Windows 询问是否终止，请输入 Y。
echo   - 或直接关闭此命令行窗口。
echo   - 或双击 stop-audio-transcribe.bat。
echo ==================================================
echo.

"%PYTHON_EXE%" -m uvicorn app.main:app --host %APP_HOST% --port %APP_PORT%
goto done

:open_existing_app
echo Audio-Transcribe 似乎已经在运行。
echo 正在打开现有网页：
echo   %APP_URL%
start "" "%APP_URL%"
echo.
echo 如需停止现有服务，请双击 stop-audio-transcribe.bat。
echo.
pause

:done
endlocal
