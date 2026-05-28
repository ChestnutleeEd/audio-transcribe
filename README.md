# Audio Transcribe

本地优先的音视频转写工作台。后端使用 FastAPI、FFmpeg、yt-dlp、faster-whisper 和本地 Whisper 模型；前端是无需构建的静态页面。适合面试录音、YouTube / Bilibili 视频、课程或会议音频的本地转录。

![Audio Transcribe 首页](docs/assets/audio-transcribe-home.png)

## 功能

- 上传本地音频/视频文件：`mp3`、`m4a`、`wav`、`flac`、`aac`、`ogg`、`mp4`、`mov`、`mkv`、`webm`、`avi`
- 粘贴 YouTube、Bilibili 等 `yt-dlp` 支持的视频链接并抽取音频
- 自动清理 YouTube 浏览记录链接里的时间参数，例如 `&t=459s`，避免卡在“准备音频来源”
- 链接任务下载成功后，会用视频标题作为任务名称；任务名称本身会保留原视频链接超链接
- 转换语言选择：自动识别、中文、日语、英语、韩语
- 输出格式多选：默认只生成 `TXT`，也可选择 `Markdown` 和 `Word`
- 可选择带时间轴或纯文本
- 可截取本地媒体的指定时间段；选择本地媒体后会自动填入完整时长
- 每个任务会显示实时处理耗时；完成、失败或停止后显示总耗时
- 任务失败会在卡片中显示错误信息，不会一直停在准备阶段
- 输出文件可下载，也可在页面中手动删除
- 支持模型选择、模型检测、模型下载、下载取消和 CUDA 失败后的 CPU 降级提示

## 运行

### 一键启动

Windows 下可以直接双击项目根目录的：

```text
start-audio-transcribe.bat
```

脚本会检测本地服务是否已启动。如果没有，会启动服务并打开：

```text
http://127.0.0.1:8000
```

### 手动启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --use-deprecated=legacy-resolver -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 使用方法

1. 打开页面后，在“新建任务”中上传本地文件，或粘贴视频链接。
2. 选择语言。大多数情况下可保持“自动识别”。
3. 选择是否带时间轴。
4. 选择输出格式。默认只选中 `TXT`；如需文档格式，可额外勾选 `Markdown` 或 `Word`。
5. 如需只转录片段，展开“截取时间段”并设置开始/结束时间。
6. 点击“开始转写”，右侧任务列表会显示进度、状态、处理耗时、模型和输出文件。
7. 链接任务完成下载后，任务标题会更新为视频名称，点击标题可回到原视频链接。

## 链接下载说明

应用会在提交任务时标准化视频链接。YouTube 链接会保留 `v` 参数并移除时间戳参数，例如：

```text
https://www.youtube.com/watch?v=ecAh4F6CjJY&t=459s
```

会转换为：

```text
https://www.youtube.com/watch?v=ecAh4F6CjJY
```

如果 `yt-dlp` 无法下载、网络不可达、代理不可用或下载超时，任务会进入失败状态并显示错误信息。

## 本地模型和运行时配置

GitHub 仓库不会包含 large-v3 模型文件。模型体积很大，`models/` 和 `origin-code/` 都会被 Git 忽略。

应用启动后会自动检测模型，检测顺序：

1. `AUDIO_TRANSCRIBE_MODEL_PATH` 指定的目录
2. `models/large-v3-local`
3. `origin-code/large-v3-local`

如果没有检测到模型，页面右侧会显示“下载模型”按钮。点击并确认后，会从 Hugging Face 下载：

```text
Systran/faster-whisper-large-v3
```

默认下载位置：

```text
models/large-v3-local
```

下载过程中会出现“取消下载”按钮。取消后，应用会中止当前下载进程，并清理该模型目录下本次产生的部分文件。

不同 faster-whisper 模型的词表文件可能是 `vocabulary.json` 或 `vocabulary.txt`，应用会兼容两种文件名。

可通过环境变量覆盖：

```powershell
$env:AUDIO_TRANSCRIBE_MODEL_PATH="D:\Projects\audio-transcribe\models\large-v3-local"
$env:AUDIO_TRANSCRIBE_DEVICE="cuda"
$env:AUDIO_TRANSCRIBE_COMPUTE_TYPE="int8_float16"
$env:AUDIO_TRANSCRIBE_FFMPEG="D:\Projects\audio-transcribe\origin-code\ffmpeg.exe"
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

如果 CUDA DLL 不在系统路径里，可以用分号分隔多个目录：

```powershell
$env:AUDIO_TRANSCRIBE_DLL_DIRS="E:\Programming\Anaconda\envs\whisper_env\Lib\site-packages\nvidia\cudnn\bin;E:\Programming\Anaconda\envs\whisper_env\Lib\site-packages\nvidia\cublas\bin"
```

当前项目优先尝试 `cuda / int8_float16`。如果任务卡片显示 `CPU / int8`，说明本次 CUDA 转写失败后已自动降级，结果仍会生成，但速度会慢一些。
