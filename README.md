# Audio Transcribe

本地优先的音视频转写工作台。后端使用 FastAPI、FFmpeg、yt-dlp、faster-whisper 和本地 Whisper 模型，前端是无需构建的静态页面。适合面试录音、YouTube / Bilibili 视频、课程或会议音频的本地转写。

![Audio Transcribe 首页](docs/assets/audio-transcribe-home.png)

## 功能

- 上传本地音频/视频文件：`mp3`、`m4a`、`wav`、`flac`、`aac`、`ogg`、`mp4`、`mov`、`mkv`、`webm`、`avi`
- 粘贴 YouTube、Bilibili 等 `yt-dlp` 支持的视频链接并抽取音频
- 自动清理 YouTube 浏览记录链接里的时间参数，例如 `&t=459s`，避免卡在“准备音频来源”
- 链接任务下载成功后，会用视频标题作为任务名称；任务名称本身会保留原视频链接
- 转写语言选择：自动识别、中文、日语、英语、韩语
- 输出格式多选：默认生成 `TXT`，也可选择 `Markdown`、`JSON`、`SRT` 和 `Word`
- 导出内容可选择 `Raw`、`Polished` 或 `Raw + Polished`；SRT 仅在开启时间轴时可用
- 可选择带时间轴或纯文本
- 可截取本地媒体的指定时间段；选择本地媒体后会自动填入完整时长
- 每个任务会显示实时处理耗时；完成、失败或停止后显示总耗时
- 任务失败会在卡片中显示错误信息，不会一直停在准备阶段
- 输出文件可下载，也可在页面中手动删除
- 支持模型选择、模型检测、模型下载进度、下载取消和 CUDA 失败后的 CPU 降级提示
- 可显式选择转录引擎：稳定 Whisper、MLX Whisper（Apple Silicon 推荐），或实验性本地大模型音频转录
- 可显式启用 Ollama polish 后处理，并选择标点修复、保守清理、日语自然断句、中文会议纪要、双语翻译等 profile
- Polish 支持 Prompt 预览和追加自定义指令；自定义指令会追加在基础安全模板之后，不会替换 raw transcript 保存逻辑
- Raw / Polished 同屏展示，支持复制、重新 Polish 和段落级对比
- 浏览器本地保存最近 5 条任务历史，便于恢复查看最近结果；长文本会截断，避免无限占用 localStorage
- 任务失败会显示错误诊断卡片，包含错误标题、处理建议和默认折叠的技术细节
- 页面提供环境检查，覆盖 faster-whisper、Whisper 模型、FFmpeg、Ollama 服务和本地 Ollama 模型

## 快速启动

### Windows

双击项目根目录里的：

```text
start-audio-transcribe.bat
```

这是 Windows 启动入口。脚本会检查 `.venv`，必要时运行 `scripts\setup-windows.ps1` 安装依赖，然后启动后端并打开：

```text
http://127.0.0.1:8000/
```

### macOS

双击项目根目录里的：

```text
start-audio-transcribe.command
```

这是 macOS 启动入口。若 macOS 提示无法打开或双击无反应，先在终端执行：

```bash
chmod +x start-audio-transcribe.command stop-audio-transcribe.command
```

然后重新双击 `start-audio-transcribe.command`。

更多启动和关闭细节见 [docs/START_AND_STOP.md](docs/START_AND_STOP.md)。

## 如何关闭

### Windows

- 在启动窗口按 `Ctrl + C`，如果 Windows 询问是否终止批处理操作，输入 `Y`。
- 或直接关闭启动命令行窗口。
- 或双击 `stop-audio-transcribe.bat`，按 PID 文件或端口停止服务。

### macOS

- 回到启动时打开的 Terminal 窗口，按 `Control + C`。
- 或关闭该 Terminal 窗口。
- 或双击 `stop-audio-transcribe.command`，按 PID 文件或端口停止服务。

## 首次使用前准备

- Python：建议使用 Python 3.10 或更新版本。Windows 发行版通常已包含虚拟环境；源码安装会在 `.venv` 中安装依赖。
- FFmpeg：音视频预处理依赖 FFmpeg。macOS 推荐 `brew install ffmpeg`；Windows 可使用发行版内置 FFmpeg，或把 `ffmpeg.exe` / `ffprobe.exe` 放到 `origin-code/`。
- Python 依赖：启动脚本会在缺少 `.venv` 时调用 `scripts/setup-windows.ps1` 或 `scripts/setup-macos.sh`。也可以手动执行 `pip install -r requirements.txt`。
- Whisper 模型：项目和发行版不会内置模型，也不会在启动脚本中自动下载模型。进入页面后选择模型并确认下载，或手动把模型放到 `models/`。
- Windows 模型路径：优先使用页面内模型下载；已有 faster-whisper 模型时可放到 `models/<model>-local/`，或用 `AUDIO_TRANSCRIBE_MODEL_PATH` 指向现有目录。
- Apple Silicon Mac：可考虑 MLX Whisper，但需要自行安装 `mlx-whisper`、准备模型并配置环境变量；启动脚本不会自动安装 MLX 依赖或下载 MLX 模型。

## 安装

### Windows

#### 方式一：下载发行版便携包

1. 打开 [GitHub Releases](https://github.com/ChestnutleeEd/audio-transcribe/releases)，下载 `AudioTranscribe-v0.1.0-windows-x64.zip`。
2. 解压 zip 到任意目录。
3. 双击 `start-audio-transcribe.bat`。

Windows 发行版已经包含 Python 虚拟环境和 FFmpeg / FFprobe，首次启动不需要手动安装 Python 依赖。发行版不内置 Whisper 模型，启动后请在页面右侧选择模型并下载，或按“本地模型”部分手动放置模型文件。

#### 方式二：从源码安装

```powershell
git clone https://github.com/ChestnutleeEd/audio-transcribe.git
cd audio-transcribe
.\scripts\setup-windows.ps1
```

源码安装会在项目目录下创建 `.venv` 并安装 Python 依赖。若需要处理链接或媒体文件，请确保系统能访问 FFmpeg，或把 `ffmpeg.exe` / `ffprobe.exe` 放到 `origin-code/`。

### macOS

#### 方式一：下载发行版便携包

1. 打开 [GitHub Releases](https://github.com/ChestnutleeEd/audio-transcribe/releases)，下载 `AudioTranscribe-v0.1.0-macos.zip`。
2. 解压 zip 到任意目录。
3. 安装系统依赖：

```bash
brew install ffmpeg
```

4. 首次运行前给启动脚本授权：

```bash
chmod +x scripts/setup-macos.sh start-audio-transcribe.command
```

macOS 发行版不内置 Python 虚拟环境。首次运行 `start-audio-transcribe.command` 时，会自动创建 `.venv` 并安装依赖。

#### 方式二：从源码安装

```bash
git clone https://github.com/ChestnutleeEd/audio-transcribe.git
cd audio-transcribe
brew install ffmpeg
chmod +x scripts/setup-macos.sh start-audio-transcribe.command
./scripts/setup-macos.sh
```

## 运行

### Windows

#### 方式一：双击启动

双击项目根目录或发行版目录里的：

```text
start-audio-transcribe.bat
```

脚本会检测本地服务是否已经启动。如果未启动，会启动服务并打开：

```text
http://127.0.0.1:8000/
```

启动窗口会保持打开。需要关闭服务时，在该窗口按 `Ctrl + C` 后输入 `Y`，或双击 `stop-audio-transcribe.bat`。

#### 方式二：命令行启动

```powershell
.\start-audio-transcribe.bat
```

#### 方式三：手动启动开发服务

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

然后在浏览器打开：

```text
http://127.0.0.1:8000
```

### macOS

#### 方式一：双击启动

双击发行版或源码目录里的：

```text
start-audio-transcribe.command
```

首次运行会自动安装 Python 依赖；之后会直接启动服务并打开浏览器。

启动 Terminal 窗口会保持打开。需要关闭服务时，在该窗口按 `Control + C`，或双击 `stop-audio-transcribe.command`。

#### 方式二：命令行启动

```bash
./start-audio-transcribe.command
```

#### 方式三：手动启动开发服务

```bash
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

然后在浏览器打开：

```text
http://127.0.0.1:8000
```

## 使用方法

1. 打开页面后，在“新建任务”中上传本地文件，或粘贴视频链接。
2. 选择语言。大多数情况下可保持“自动识别”。
3. 选择是否带时间轴。
4. 选择输出格式。默认选中 `TXT`，也可额外勾选 `Markdown`、`JSON`、`SRT` 或 `Word`。SRT 需要开启时间轴。
5. 如启用 Polish，选择模型和 profile。默认优先使用 `gemma4:12b-it-qat`；如果本地没有该模型，可以改用 `gemma3:1b`。
6. 高级用户可以展开 Prompt 预览，并追加自定义指令，例如“保留语气词”“不要翻译”“更适合字幕”。追加指令会保存在当前浏览器。
7. 如需只转写片段，展开“截取时间段”并设置开始 / 结束时间。
8. 点击“开始转写”，右侧任务列表会显示进度、状态、阶段耗时、模型、raw transcript、polished transcript 和输出文件。
9. 链接任务完成下载后，任务标题会更新为视频名称，点击标题可回到原视频链接。

## Ollama 和本地大模型

Ollama 是可选能力。稳定 ASR 仍由 `faster-whisper` 完成，并继续支持逐段时间轴。Ollama 在当前阶段有两类用途：

- `本地大模型音频转录`：实验性转录引擎。用户选择该引擎时，应用会尝试通过 Ollama 使用所选本地多模态模型直接处理音频；如果 direct audio 调用失败，任务会失败并显示原因，不会自动改用 Whisper。
- `Polish 转录结果`：独立可选后处理。Whisper、MLX Whisper 或本地大模型音频转录的结果都可以启用 polish。polish 失败不会覆盖或破坏 raw transcript，任务会保留原始结果并在 warnings 中说明失败原因。

当前 Ollama REST API 的稳定文档主要覆盖文本输入和 `images` 字段。应用不会把音频 base64 硬塞进 prompt，也不会用图片字段冒充音频；如果当前 Ollama HTTP API 不支持所选模型的直接音频输入，会返回明确错误。

## MLX Whisper

MLX Whisper 是可选能力，适用于 macOS Apple Silicon。应用只做配置、检测、选择和调用，不会安装 `mlx-whisper`，也不会下载 MLX 模型。

可用配置示例：

```bash
AUDIO_TRANSCRIBE_MLX_WHISPER_ENABLED=1
AUDIO_TRANSCRIBE_MLX_WHISPER_MODEL=/Users/me/models/whisper-large-v3-mlx
AUDIO_TRANSCRIBE_MLX_WHISPER_LABEL=whisper-large-v3-mlx
AUDIO_TRANSCRIBE_MLX_WHISPER_LANGUAGE=auto
```

也可以在页面里选择 `MLX Whisper（Apple Silicon 推荐）` 后填写本地模型目录或已预先缓存的 Hugging Face repo id。为了避免自动下载，repo id 调用时会启用 Hugging Face 离线模式；如模型未缓存，任务会失败并显示明确提示。

### 安装和启动 Ollama

macOS 可从 Ollama 官网安装，或使用 Homebrew：

```bash
brew install ollama
ollama serve
```

如果 Ollama 已作为桌面应用运行，通常不需要手动执行 `ollama serve`。默认服务地址是：

```text
http://localhost:11434
```

可通过环境变量覆盖：

```bash
export OLLAMA_BASE_URL="http://localhost:11434"
```

### 下载 Ollama 模型

可以在页面中确认下载，也可以手动执行：

```bash
ollama pull gemma4:12b-it-qat
ollama pull gemma3:1b
```

`gemma4:12b-it-qat` 是默认 direct audio 转录模型，也是默认 polish 模型；`gemma3:1b` 是轻量 polish 备用模型。Ollama 模型由 Ollama 自己管理，不会下载到项目仓库。

### Polish 分批处理

Ollama polish 会把较长的转录结果按 segment 分批处理，降低小模型漏段、合并段落或输出截断的概率。默认批大小：

- `gemma3:1b`：5 个 segments
- `gemma4:12b-it-qat`：10 个 segments
- 其他模型：8 个 segments

可以通过环境变量覆盖：

```bash
OLLAMA_POLISH_BATCH_SIZE=5 .venv/bin/uvicorn app.main:app --reload
```

每个 batch 会独立调用 Ollama structured output，并独立校验返回结果。如果某个 batch polish 失败，该批次会保留原始转录文本，其他 batch 会继续处理。任务仍会完成，失败批次会写入任务 warnings 和 events。

### Polish Profiles

内置 profiles 集中定义在 `app/services/polish_profiles.py`：

- 标点修复：只补标点和自然断句，尽量不改原文。
- 保守清理：去除明显口癖、重复和识别噪声，不改核心语义。
- 日语自然断句：适合日语新闻、访谈和视频字幕。
- 中文会议纪要：把中文转录整理成结构化纪要，要求不编造参会人、日期或结论。
- 双语翻译：保留原文，并根据原文语言补充中文或英文翻译。

Prompt 预览会展示当前 profile 的基础指令。追加自定义指令只会附加到基础指令之后，不会替换结构化 JSON、安全校验和 raw transcript 保存逻辑。

### 导出格式

- `TXT`：按导出范围输出纯文本，可包含时间轴。
- `Markdown`：包含 metadata、Raw transcript、Polished transcript 区块。
- `JSON`：包含 metadata、segments、rawText、polishedText 和参数配置。
- `SRT`：仅在开启时间轴时可用；如果选择 `Polished` 但没有 polished transcript，任务会提示并安全降级导出 raw。
- `Word`：生成基础 `.docx` 文档。

导出范围可选择 `Raw`、`Polished` 或 `Raw + Polished`。无论 Polish 是否成功，raw transcript 都会优先保留。

## 常见问题

### 1. 双击 `.command` 没反应或提示无法打开

macOS 可能没有给脚本执行权限。进入项目目录后执行：

```bash
chmod +x start-audio-transcribe.command stop-audio-transcribe.command
```

如果仍被系统拦截，可右键脚本选择“打开”，或在“系统设置 > 隐私与安全性”中允许本次打开。

### 2. 端口被占用

Audio-Transcribe 默认使用 `127.0.0.1:8000`。如果启动窗口提示 `address already in use`，说明 8000 端口已有程序在监听。先关闭另一个程序，或运行：

- Windows：双击 `stop-audio-transcribe.bat`
- macOS：双击 `stop-audio-transcribe.command`

停止脚本会优先使用 `data/tmp/audio-transcribe-server.pid`，没有 PID 时再检查 8000 端口。

### 3. 页面打不开

确认启动窗口仍在运行，并手动打开：

```text
http://127.0.0.1:8000/
```

如果浏览器仍打不开，查看启动窗口是否有 Python、依赖、FFmpeg、端口占用或模型路径错误。

### 4. 启动后不知道怎么关闭

Windows 在启动窗口按 `Ctrl + C` 后输入 `Y`，或双击 `stop-audio-transcribe.bat`。macOS 在启动 Terminal 窗口按 `Control + C`，或双击 `stop-audio-transcribe.command`。

### 5. 清空历史后仍显示旧任务

页面最近任务历史存放在浏览器 localStorage，后端输出文件存放在 `data/jobs/`。如果清空页面历史后仍看到旧任务，先刷新页面；如果是输出文件仍存在，需要在页面中删除对应输出，或手动检查 `data/jobs/`。

### 6. Mac 上 faster-whisper large-v3 很慢

`large-v3` 体积大、资源占用高，在 MacBook Air 等设备上会明显变慢。日常建议先用 `small` 或 `medium`。Apple Silicon Mac 可以考虑自行安装并配置 MLX Whisper，但项目不会自动安装 MLX 依赖或下载 MLX 模型。

### 7. 模型未配置或模型路径不存在

进入页面右侧模型区选择模型并确认下载，或把 faster-whisper 模型文件放入 `models/<model>-local/`。也可以用环境变量指定已有模型目录：

```bash
AUDIO_TRANSCRIBE_MODEL_PATH=/path/to/model .venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### 8. FFmpeg 未安装

macOS 执行：

```bash
brew install ffmpeg
```

Windows 可使用发行版内置 FFmpeg，或把 `ffmpeg.exe` / `ffprobe.exe` 放到 `origin-code/`，也可设置 `AUDIO_TRANSCRIBE_FFMPEG` 指向可执行文件。

## 常见错误

- `OLLAMA_NOT_RUNNING`：启动 Ollama 桌面应用，或执行 `ollama serve`。
- `OLLAMA_MODEL_MISSING`：执行 `ollama pull gemma4:12b-it-qat` 或 `ollama pull gemma3:1b`，也可以切换到已安装模型。
- `FFMPEG_MISSING`：安装 FFmpeg，或设置 `AUDIO_TRANSCRIBE_FFMPEG` 指向可执行文件。
- `WHISPER_MODEL_MISSING`：在页面选择 Whisper 模型并确认下载，或手动把模型文件放入 `models/` 对应目录。
- `INVALID_AUDIO_FILE`：确认文件能正常播放，或先转换成常见音频格式后重试。
- `TRANSCRIBE_TIMEOUT`：检查网络、模型运行状态，或先截取较短音频重试。
- `POLISH_EMPTY_RESPONSE`：切换到保守清理 profile 或更轻量模型后重新 Polish。
- `TASK_CANCELLED`：任务已停止，需要时重新提交。

### Mock / Dry Run 模式

开发或验收 UI 流程时，可以开启 mock 模式：

```bash
AUDIO_TRANSCRIBE_MOCK=1 .venv/bin/uvicorn app.main:app --reload
```

Mock 模式下：

- 不调用真实 `faster-whisper`
- 不调用真实 Ollama
- Whisper 转录返回固定 mock segments
- 本地大模型音频转录返回固定 mock transcription
- Ollama polish 返回固定 mock polished segments
- Ollama 模型检测会模拟 `gemma4:12b-it-qat` 和 `gemma3:1b` 已存在
- Ollama pull 会模拟下载进度，并支持取消
- 前端会显示“Mock 模式：不会调用真实模型”

如需验证 polish 失败但保留原始转录结果：

```bash
AUDIO_TRANSCRIBE_MOCK=1 AUDIO_TRANSCRIBE_MOCK_POLISH_FAIL=1 .venv/bin/uvicorn app.main:app --reload
```

任务卡片会显示 events 时间线，用于观察 job created、模型检查、转录、polish 和导出等关键阶段。

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

## 本地模型

GitHub 仓库和发行版便携包都不会内置 Whisper 模型。模型体积较大，首次运行后请在页面右侧选择模型并点击“下载模型”，也可以手动下载并放入 `models/`。`models/` 和 `origin-code/` 都会被 Git 忽略。

应用启动后会自动检测模型，检测顺序：

1. `AUDIO_TRANSCRIBE_MODEL_PATH` 指定的目录
2. `models/large-v3-local`
3. `origin-code/large-v3-local`

如果没有检测到模型，页面右侧会显示“下载模型”按钮。点击并确认后，应用会从 Hugging Face 下载所选模型。

### 手动下载模型

手动下载时，把 Hugging Face 仓库里的必要文件放到对应目录。必要文件是：

- `config.json`
- `model.bin`
- `tokenizer.json`
- `vocabulary.json` 或 `vocabulary.txt`

| 页面选项 | Hugging Face 链接 | 预计大小 | 放置目录 |
| --- | --- | ---: | --- |
| `faster-whisper tiny` | [Systran/faster-whisper-tiny](https://huggingface.co/Systran/faster-whisper-tiny/tree/main) | 75 MB | `models/tiny-local/` |
| `faster-whisper base` | [Systran/faster-whisper-base](https://huggingface.co/Systran/faster-whisper-base/tree/main) | 141 MB | `models/base-local/` |
| `faster-whisper small` | [Systran/faster-whisper-small](https://huggingface.co/Systran/faster-whisper-small/tree/main) | 464 MB | `models/small-local/` |
| `faster-whisper medium` | [Systran/faster-whisper-medium](https://huggingface.co/Systran/faster-whisper-medium/tree/main) | 1.43 GB | `models/medium-local/` |
| `faster-whisper large-v3` | [Systran/faster-whisper-large-v3](https://huggingface.co/Systran/faster-whisper-large-v3/tree/main) | 2.88 GB | `models/large-v3-local/` |

例如手动下载 `small` 时，目录结构应类似：

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

### 运行时配置

可以通过环境变量覆盖模型、设备和 FFmpeg 路径：

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

当前项目优先尝试 `cuda / int8_float16`。如果任务卡片显示 `CPU / int8`，说明本次 CUDA 转写失败后已经自动降级，结果仍会生成，但速度会慢一些。

## 手动测试清单

1. 启动服务后打开页面，确认环境检查能显示 Python、faster-whisper、FFmpeg、Whisper 模型和 Ollama 状态。
2. 上传本地音频，选择 Whisper、TXT/Markdown/JSON，提交后确认任务进入阶段状态并最终完成。
3. 开启 Polish，选择不同 profile，确认 raw transcript 和 polished transcript 同时显示，且可分别复制。
4. 点击“对比”，确认能看到段落级 raw/polished 对比；差异较大时会提示使用保守清理。
5. 输入追加 Polish 指令，刷新页面后确认最近一次指令仍保留。
6. 选择 SRT 并关闭时间轴，确认 SRT 被禁用；开启时间轴后确认 SRT 可导出。
7. 停止 Ollama 后尝试启用 Polish，确认页面显示错误诊断卡片且 App 不崩溃。
8. 任务运行时连续点击开始，确认不会创建并发任务；点击停止后确认任务进入 cancelled。
9. 完成后点击“重新 Polish”，确认不重新转录，且 raw transcript 保留。
10. 完成 6 次 mock 任务，确认最近历史最多保留 5 条，并可点击恢复查看。

## 项目目录说明

- `start-audio-transcribe.bat`：Windows 启动入口。
- `start-audio-transcribe.command`：macOS 启动入口。
- `stop-audio-transcribe.bat`：Windows 停止脚本。
- `stop-audio-transcribe.command`：macOS 停止脚本。
- `models/`：本地 Whisper / faster-whisper 模型目录，Git 默认忽略。
- `output/`：保留给导出或外部整理输出使用。
- `data/`：运行时任务、上传文件、临时文件和 PID 文件目录，Git 默认忽略其中运行时内容。
- `docs/`：补充文档、发行说明和图片资源。
