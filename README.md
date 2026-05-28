# Audio Transcribe

本地优先的面试录音转写工作台。后端使用 FastAPI、FFmpeg、faster-whisper 和本地 `large-v3-local` 模型；前端是无需构建的静态页面。

## 第一版功能

- 上传本地音频/视频文件：`mp3`、`m4a`、`wav`、`flac`、`aac`、`ogg`、`mp4`、`mov`、`mkv`、`webm`、`avi`
- 粘贴 YouTube、Bilibili 等 `yt-dlp` 支持的视频链接并抽取音频
- 转换语言选择：自动识别、中文、日语、英语、韩语
- 输出格式多选：Word、TXT、Markdown
- 可选择是否带时间轴
- 默认转写整段音视频；选择本地媒体后会自动把开始时间设为 `00:00:00`、结束时间设为媒体时长，也可手动选择片段
- 下载转录文件后，服务端会删除对应输出文件，减少磁盘占用

## 运行

### 一键启动

Windows 下可以直接双击项目根目录的：

```text
start-audio-transcribe.bat
```

它会自动检测服务是否已启动；如果没有，会启动本地服务并打开浏览器。

### 手动启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

然后打开：

```text
http://127.0.0.1:8000
```

## 本地模型和运行时配置

GitHub 仓库不会包含 large-v3 模型文件。模型体积很大，`models/` 和 `origin-code/` 都会被 Git 忽略。

应用启动后会自动检测模型，检测顺序：

1. `AUDIO_TRANSCRIBE_MODEL_PATH` 指定的目录
2. `models/large-v3-local`
3. `origin-code/large-v3-local`

页面右侧会显示模型状态，并提供“重新检测”按钮。点击后会主动检查本地模型是否存在。

如果没有检测到模型，页面右侧会显示“下载模型”按钮。点击并确认后，会从 Hugging Face 下载：

```text
Systran/faster-whisper-large-v3
```

默认下载位置：

```text
models/large-v3-local
```

当前兼容的旧模型路径：

```text
origin-code/large-v3-local
```

可通过环境变量覆盖：

```powershell
$env:AUDIO_TRANSCRIBE_MODEL_PATH="D:\Projects\audio-transcribe\origin-code\large-v3-local"
$env:AUDIO_TRANSCRIBE_DEVICE="cuda"
$env:AUDIO_TRANSCRIBE_COMPUTE_TYPE="int8_float16"
$env:AUDIO_TRANSCRIBE_FFMPEG="D:\Projects\audio-transcribe\origin-code\ffmpeg.exe"
uvicorn app.main:app --reload
```

如果 CUDA DLL 不在系统路径里，可以用分号分隔多个目录：

```powershell
$env:AUDIO_TRANSCRIBE_DLL_DIRS="E:\Programming\Anaconda\envs\whisper_env\Lib\site-packages\nvidia\cudnn\bin;E:\Programming\Anaconda\envs\whisper_env\Lib\site-packages\nvidia\cublas\bin"
```

## GitHub 上传

第一版工程化文件已经准备好。上传前需要你提供 GitHub 仓库地址，或者确认要我用 `gh` 创建一个新仓库。
