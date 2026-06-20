# Audio-Transcribe 启动和关闭说明

本文面向普通使用者，说明 Windows 和 macOS 上如何启动、关闭、处理端口占用和脚本权限问题。

## Windows 启动

双击项目根目录里的：

```text
start-audio-transcribe.bat
```

这是 Windows 启动入口。脚本会：

1. 切换到项目目录。
2. 检查 `http://127.0.0.1:8000/` 是否已经有服务运行。
3. 检查 `.venv\Scripts\python.exe` 是否存在。
4. 如果虚拟环境不存在，调用 `scripts\setup-windows.ps1` 安装依赖。
5. 启动 FastAPI 后端，并打开浏览器访问 `http://127.0.0.1:8000/`。

启动窗口需要保持打开。关闭窗口或按 `Ctrl + C` 会停止前台运行的服务。

## macOS 启动

双击项目根目录里的：

```text
start-audio-transcribe.command
```

这是 macOS 启动入口。脚本会：

1. 切换到项目目录。
2. 检查 `.venv/bin/python` 是否存在且可执行。
3. 如果虚拟环境不存在，调用 `scripts/setup-macos.sh` 安装依赖。
4. 检查 `http://127.0.0.1:8000/` 是否已经有服务运行。
5. 启动 FastAPI 后端，写入 PID 文件，并打开浏览器访问 `http://127.0.0.1:8000/`。
6. 等待后端进程结束，并在 `Control + C` 或 Terminal 退出时清理子进程。

如果 macOS 提示无法打开或双击无反应，进入项目目录后执行：

```bash
chmod +x start-audio-transcribe.command stop-audio-transcribe.command
```

Apple Silicon Mac 可以优先考虑 MLX Whisper，但需要自行安装 `mlx-whisper`、准备模型并配置环境变量。启动脚本不会自动安装 MLX 依赖，也不会自动下载模型。

## Windows 关闭

推荐方式：

```text
在启动窗口按 Ctrl + C，然后输入 Y
```

也可以双击：

```text
stop-audio-transcribe.bat
```

停止脚本会先检查 `data\tmp\audio-transcribe-server.pid`，再检查 8000 端口。如果发现进程，会显示 PID 并执行 `taskkill /PID ... /F`。

## macOS 关闭

推荐方式：

```text
回到启动 Terminal 窗口，按 Control + C
```

也可以双击：

```text
stop-audio-transcribe.command
```

停止脚本会先检查 `data/tmp/audio-transcribe-server.pid`，再用 `lsof` 检查 8000 端口。如果发现进程，会显示 PID 并执行 `kill`。

## 端口占用处理

Audio-Transcribe 默认监听：

```text
127.0.0.1:8000
```

如果启动窗口出现 `address already in use`，说明端口 8000 已被占用。处理方式：

- 如果是之前启动的 Audio-Transcribe，运行对应平台的停止脚本。
- 如果是其他程序占用，请关闭该程序，或改用手动启动命令并指定其他端口。

手动指定端口示例：

```bash
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Windows PowerShell 示例：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## PID 文件说明

macOS 启动脚本会把后端进程 PID 写入：

```text
data/tmp/audio-transcribe-server.pid
```

停止脚本会优先读取这个文件。若 PID 文件不存在、为空或进程已退出，停止脚本会检查 8000 端口作为兜底。

Windows 默认以前台方式运行服务，方便通过关闭窗口或 `Ctrl + C` 直接停止。停止脚本同样会检查 PID 文件和 8000 端口，因此也可以处理残留服务。

## 常见问题

### 页面打不开

先确认启动窗口仍在运行，再手动打开：

```text
http://127.0.0.1:8000/
```

如果仍打不开，查看启动窗口是否提示端口占用、Python 缺失、依赖安装失败或 FFmpeg 不可用。

### 依赖缺失

Windows 运行：

```powershell
.\scripts\setup-windows.ps1
```

macOS 运行：

```bash
brew install ffmpeg
./scripts/setup-macos.sh
```

### 模型缺失

项目不会内置 Whisper 模型，启动脚本也不会自动下载模型。进入页面后选择模型并确认下载，或把模型文件手动放入 `models/<model>-local/`。

### Mac 上 large-v3 很慢

`faster-whisper large-v3` 质量高但体积大，在轻薄 Mac 上会很慢。日常建议先使用 `small` 或 `medium`。Apple Silicon 用户可自行配置 MLX Whisper。
