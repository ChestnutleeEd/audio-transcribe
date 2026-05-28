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
- 支持模型选择、模型检测、模型下载进度、下载取消和 CUDA 失败后的 CPU 降级提示

## 安装和运行

### 发行版便携包

首个发行版建议使用 `v0.1.0`。安装包不内置 Whisper 模型，首次运行后在页面右侧按需下载模型。

从 GitHub Releases 下载对应系统的便携包：

- Windows x64：`AudioTranscribe-v0.1.0-windows-x64.zip`
- macOS：`AudioTranscribe-v0.1.0-macos.zip`

Windows 便携包：

1. 解压 zip 到任意目录。
2. 双击 `start-audio-transcribe.bat`。
3. 如果包里已有 `.venv`，会直接启动；如果没有，会自动创建环境并安装依赖。
4. 浏览器会打开 `http://127.0.0.1:8000`。

macOS 便携包：

1. 解压 zip 到任意目录。
2. 先安装系统依赖：

```bash
brew install ffmpeg
```

3. 首次运行：

```bash
chmod +x scripts/setup-macos.sh start-audio-transcribe.command
./start-audio-transcribe.command
```

4. 脚本会自动创建 `.venv`、安装 Python 依赖并打开 `http://127.0.0.1:8000`。

### 命令安装

Windows PowerShell：

```powershell
git clone https://github.com/ChestnutleeEd/audio-transcribe.git
cd audio-transcribe
.\scripts\setup-windows.ps1
.\start-audio-transcribe.bat
```

macOS Terminal：

```bash
git clone https://github.com/ChestnutleeEd/audio-transcribe.git
cd audio-transcribe
brew install ffmpeg
chmod +x scripts/setup-macos.sh start-audio-transcribe.command
./scripts/setup-macos.sh
./start-audio-transcribe.command
```

### 本地开发运行

Windows 下可以直接双击项目根目录的：

```text
start-audio-transcribe.bat
```

脚本会检测本地服务是否已启动。如果没有，会启动服务并打开：

```text
http://127.0.0.1:8000
```

也可以手动启动：

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

GitHub 仓库和发行版便携包都不会内置 Whisper 模型。模型体积较大，首次运行后请在页面右侧选择模型并点击“下载模型”，或按下表手动下载。`models/` 和 `origin-code/` 都会被 Git 忽略。

应用启动后会自动检测模型，检测顺序：

1. `AUDIO_TRANSCRIBE_MODEL_PATH` 指定的目录
2. `models/large-v3-local`
3. `origin-code/large-v3-local`

如果没有检测到模型，页面右侧会显示“下载模型”按钮。点击并确认后，会从 Hugging Face 下载所选模型。

### 手动下载模型

手动下载时，把 Hugging Face 仓库里的必要文件放到对应目录。必要文件是：

- `config.json`
- `model.bin`
- `tokenizer.json`
- `vocabulary.json` 或 `vocabulary.txt`

| 页面选项 | Hugging Face 链接 | 预估大小 | 放置目录 |
| --- | --- | ---: | --- |
| `faster-whisper tiny` | [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny/tree/main) | 75 MB | `models/tiny-local/` |
| `faster-whisper base` | [Systran/faster-whisper-base](https://huggingface.co/Systran/faster-whisper-base/tree/main) | 141 MB | `models/base-local/` |
| `faster-whisper small` | [Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small/tree/main) | 464 MB | `models/small-local/` |
| `faster-whisper medium` | [Systran/faster-whisper-medium](https://huggingface.co/Systran/faster-whisper-medium/tree/main) | 1.43 GB | `models/medium-local/` |
| `faster-whisper large-v3` | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3/tree/main) | 2.88 GB | `models/large-v3-local/` |

示例：如果手动下载 `small`，目录结构应类似：

```text
models/
  small-local/
    config.json
    model.bin
    tokenizer.json
    vocabulary.txt
```

下载过程中会显示阶段进度条、百分比和已下载大小。进度不是只按文件数量计算：应用会先解析 Hugging Face 文件清单，再按必要文件大小、磁盘写入和下载活动综合展示，避免 `model.bin` 这类大文件下载时长时间停在个位数。下载时也会出现“取消下载”按钮；取消后，应用会中止当前下载进程，并清理该模型目录下本次产生的部分文件。

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
