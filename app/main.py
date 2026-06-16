from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.schemas import (
    AppOptions,
    JobState,
    JobStatus,
    ModelSelection,
    OllamaModelCheck,
    OllamaPreflightStatus,
    OllamaPullRequest,
    OllamaPullStatus,
    OllamaServiceStatus,
    OptionItem,
    OutputFile,
    OutputFormat,
    TranscriptionEngine,
)
from app.services.exporters import TranscriptSegment, export_transcript
from app.services.jobs import Job, job_store
from app.services.media import (
    OperationCanceled,
    SUPPORTED_UPLOAD_SUFFIXES,
    download_audio,
    ensure_runtime_dirs,
    normalize_audio,
    normalize_source_url,
    safe_stem,
)
from app.services.model_manager import (
    current_model_id,
    download_model,
    model_status,
    request_model_download_cancel,
    select_model,
    set_runtime_device,
)
from app.services.ollama_client import OllamaError
from app.services.ollama_model_manager import (
    check_model as check_ollama_model,
    ollama_status,
    preflight as ollama_preflight,
    pull_model as pull_ollama_model,
    pull_status as ollama_pull_status,
    request_pull_cancel as request_ollama_pull_cancel,
)
from app.services.ollama_provider import polish_segments, transcribe_audio_direct
from app.services.transcriber import transcribe_audio


app = FastAPI(title=settings.app_name)
executor = ThreadPoolExecutor(max_workers=1)
ollama_executor = ThreadPoolExecutor(max_workers=1)


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_time_offset(value: str | None) -> float:
    if not value:
        return 0.0
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        return 0.0
    try:
        numbers = [float(part) for part in parts]
    except ValueError:
        return 0.0
    if len(numbers) == 2:
        minutes, seconds = numbers
        return minutes * 60 + seconds
    hours, minutes, seconds = numbers
    return hours * 3600 + minutes * 60 + seconds


def offset_segments(segments: list[TranscriptSegment], offset_seconds: float) -> list[TranscriptSegment]:
    if offset_seconds <= 0:
        return segments
    return [
        TranscriptSegment(
            start=segment.start + offset_seconds,
            end=segment.end + offset_seconds,
            text=segment.text,
        )
        for segment in segments
    ]


def parse_formats(raw_formats: list[str] | str) -> list[OutputFormat]:
    if isinstance(raw_formats, str):
        items = [item.strip() for item in raw_formats.split(",")]
    else:
        items = raw_formats
    formats = [OutputFormat(item) for item in items if item]
    if not formats:
        raise ValueError("请至少选择一种转录文件格式")
    return formats


def unlink_file(path: Path) -> None:
    if path.exists() and path.is_file():
        path.unlink()


def build_status(job: Job) -> JobStatus:
    return JobStatus(
        id=job.id,
        state=job.state,
        progress=job.progress,
        message=job.message,
        source_label=job.source_label,
        source_url=job.source_url,
        language=job.language,
        start_time=job.start_time,
        end_time=job.end_time,
        processing_started_at=job.processing_started_at,
        processing_finished_at=job.processing_finished_at,
        transcription_engine=job.transcription_engine,
        whisper_model_id=job.whisper_model_id,
        transcription_model_id=job.transcription_model_id,
        enable_polish=job.enable_polish,
        polish_model_id=job.polish_model_id,
        model_label=job.model_label,
        formats=job.formats,
        include_timestamps=job.include_timestamps,
        created_at=job.created_at,
        outputs=job.outputs,
        warnings=job.warnings,
        events=job.events,
        error=job.error,
    )


def is_job_canceled(job_id: str) -> bool:
    current = job_store.get(job_id)
    return current is None or current.cancel_requested


def planned_model_label(model_id: str | None = None) -> str:
    model_id = model_id or current_model_id()
    return f"{model_id}（计划 {settings.device}/{settings.compute_type}）"


def loaded_model_label(model_meta: dict[str, str] | None) -> str:
    if not model_meta:
        return planned_model_label()
    model_id = model_meta.get("model_id", current_model_id())
    device = model_meta.get("device", settings.device)
    compute_type = model_meta.get("compute_type", settings.compute_type)
    return f"{model_id}（{device}/{compute_type}）"


def append_job_warning(job_id: str, warning: str) -> None:
    job = job_store.get(job_id)
    if job is None:
        return
    warnings = [*job.warnings, warning]
    job_store.update(job_id, warnings=warnings)
    job_store.add_event(job_id, warning, "warning")


def add_event(job_id: str, message: str, level: str = "info") -> None:
    job_store.add_event(job_id, message, level)


def mock_whisper_segments() -> list[TranscriptSegment]:
    return [
        TranscriptSegment(start=0.0, end=2.4, text="这是 mock Whisper 转录的第一段。"),
        TranscriptSegment(start=2.4, end=5.8, text="这是 mock Whisper 转录的第二段，用于验证导出和时间线。"),
    ]


def run_job(
    job_id: str,
    source_path: Path | None,
    source_url: str | None,
    base_name: str,
    language: str,
    formats: list[OutputFormat],
    include_timestamps: bool,
    start_time: str | None,
    end_time: str | None,
    model_id: str,
    transcription_engine: TranscriptionEngine,
    transcription_model_id: str | None,
    enable_polish: bool,
    polish_model_id: str | None,
) -> None:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        return

    try:
        job_store.update(job_id, processing_started_at=utc_now_iso(), processing_finished_at=None)
        add_event(job_id, "job started")
        if job.cancel_requested:
            job_store.update(
                job_id,
                state=JobState.canceled,
                progress=100,
                message="已取消排队任务",
                processing_finished_at=utc_now_iso(),
            )
            return

        job_store.update(job_id, state=JobState.running, progress=8, message="准备音频来源")
        work_dir = job.work_dir
        media_path = source_path
        if media_path is None and source_url:
            if settings.mock_mode:
                add_event(job_id, "mock mode skipped source download")
                media_path = work_dir / "mock_source.wav"
            else:
                media_path = download_audio(source_url, work_dir, lambda: is_job_canceled(job_id))
                base_name = safe_stem(media_path.name)
                job_store.update(job_id, source_label=Path(media_path).stem)

        if media_path is None:
            raise ValueError("缺少上传文件或视频链接")

        if is_job_canceled(job_id):
            raise OperationCanceled("任务已停止")

        job_store.update(job_id, progress=24, message="准备 16k 单声道音频")
        wav_path = work_dir / "input_16k.wav"
        if settings.mock_mode:
            add_event(job_id, "mock mode skipped audio normalization")
        else:
            normalize_audio(media_path, wav_path, start_time, end_time, lambda: is_job_canceled(job_id))

        if transcription_engine == TranscriptionEngine.whisper:
            job_store.update(job_id, progress=42, message=f"加载 {model_id} 模型")
            add_event(job_id, "whisper transcription started")

            def update_transcribe_status(stage: str, model_meta: dict[str, str] | None) -> None:
                if is_job_canceled(job_id):
                    return
                if stage == "loading_model":
                    active_model_id = model_meta.get("model_id", model_id) if model_meta else model_id
                    job_store.update(job_id, progress=42, message=f"加载 {active_model_id} 模型")
                elif stage == "model_loaded":
                    label = loaded_model_label(model_meta)
                    if model_meta:
                        set_runtime_device(
                            model_meta.get("device", settings.device),
                            model_meta.get("compute_type", settings.compute_type),
                        )
                    job_store.update(
                        job_id,
                        progress=50,
                        message="模型已加载，开始转写",
                        model_label=label,
                    )
                elif stage == "transcribing":
                    label = loaded_model_label(model_meta)
                    job_store.update(
                        job_id,
                        progress=58,
                        message="正在转写音频",
                        model_label=label,
                    )

                elif stage == "fallback_cpu":
                    label = loaded_model_label(model_meta)
                    if model_meta:
                        set_runtime_device(
                            model_meta.get("device", "cpu"),
                            model_meta.get("compute_type", "int8"),
                        )
                    job_store.update(
                        job_id,
                        progress=52,
                        message="CUDA 转写进程异常退出，正在切换 CPU 重试",
                        model_label=label,
                    )

            try:
                if settings.mock_mode:
                    segments = mock_whisper_segments()
                    job_store.update(job_id, progress=58, message="Mock Whisper 转录完成", model_label=f"{model_id}（mock）")
                else:
                    segments = transcribe_audio(
                        wav_path,
                        language,
                        lambda: is_job_canceled(job_id),
                        update_transcribe_status,
                        model_id,
                    )
                add_event(job_id, "whisper transcription completed")
            except Exception as exc:
                add_event(job_id, f"whisper transcription failed: {exc}", "error")
                raise
        elif transcription_engine == TranscriptionEngine.ollama_audio:
            active_transcription_model = transcription_model_id or settings.default_ollama_transcription_model_id
            job_store.update(
                job_id,
                progress=50,
                message=f"正在使用 {active_transcription_model} 直接转录音频",
                model_label=f"{active_transcription_model}（Ollama direct audio，实验性）",
            )
            add_event(job_id, "ollama direct audio started")
            try:
                direct_result = transcribe_audio_direct(wav_path, active_transcription_model)
            except OllamaError as exc:
                unlink_file(wav_path)
                add_event(job_id, f"ollama direct audio failed: {exc}", "error")
                job_store.update(
                    job_id,
                    state=JobState.failed,
                    progress=100,
                    message=f"Gemma 4 12B direct audio transcription failed: {exc}",
                    error=str(exc),
                    processing_finished_at=utc_now_iso(),
                )
                return
            segments = direct_result.segments
            add_event(job_id, "ollama direct audio completed")
            for warning in direct_result.warnings:
                append_job_warning(job_id, warning)
        else:
            raise ValueError(f"不支持的转录引擎: {transcription_engine}")

        if not segments:
            raise RuntimeError("没有识别到可用文本")

        if is_job_canceled(job_id):
            raise OperationCanceled("任务已停止")

        if enable_polish:
            active_polish_model = polish_model_id or settings.default_ollama_polish_model_id
            job_store.update(
                job_id,
                progress=74,
                message=f"正在使用 {active_polish_model} 整理转录文本",
            )
            add_event(job_id, "polish started")
            polish_result = polish_segments(segments, active_polish_model)
            if polish_result.success:
                segments = polish_result.segments
                job_store.update(job_id, progress=80, message="文本整理完成")
                add_event(job_id, "polish completed")
            elif polish_result.warning:
                append_job_warning(job_id, polish_result.warning)
                job_store.update(job_id, progress=80, message="文本整理失败，已保留原始转录结果")
                add_event(job_id, "polish failed", "warning")

        job_store.update(job_id, progress=82, message="生成转录文件")
        segments = offset_segments(segments, parse_time_offset(start_time))
        output_paths = export_transcript(work_dir, base_name, formats, segments, include_timestamps)
        add_event(job_id, "export generated")
        outputs = [
            OutputFile(
                name=path.name,
                format=OutputFormat(path.suffix.lstrip(".")),
                bytes=path.stat().st_size,
                download_url=f"/api/jobs/{job_id}/download/{path.name}",
            )
            for path in output_paths
        ]

        for temporary in [wav_path]:
            unlink_file(temporary)

        job_store.update(
            job_id,
            state=JobState.completed,
            progress=100,
            message="转录完成，可下载或手动删除转录文件",
            outputs=outputs,
            processing_finished_at=utc_now_iso(),
        )
    except OperationCanceled as exc:
        add_event(job_id, str(exc), "warning")
        job_store.update(
            job_id,
            state=JobState.canceled,
            progress=100,
            message=str(exc),
            error=None,
            processing_finished_at=utc_now_iso(),
        )
    except Exception as exc:
        add_event(job_id, f"job failed: {exc}", "error")
        job_store.update(
            job_id,
            state=JobState.failed,
            progress=100,
            message="任务失败",
            error=str(exc),
            processing_finished_at=utc_now_iso(),
        )


@app.on_event("startup")
def startup() -> None:
    ensure_runtime_dirs()


@app.get("/api/options", response_model=AppOptions)
def options() -> AppOptions:
    return AppOptions(
        languages=[
            OptionItem(value="auto", label="自动识别"),
            OptionItem(value="zh", label="中文"),
            OptionItem(value="ja", label="日语"),
            OptionItem(value="en", label="英语"),
            OptionItem(value="ko", label="韩语"),
        ],
        formats=[
            OptionItem(value="txt", label="TXT"),
            OptionItem(value="md", label="Markdown"),
            OptionItem(value="docx", label="Word"),
        ],
        timestamp_modes=[
            OptionItem(value="true", label="带时间轴"),
            OptionItem(value="false", label="纯文本"),
        ],
        supported_sources=["upload", "url"],
    )


@app.get("/api/model")
def get_model_status():
    return model_status()


@app.post("/api/model/select")
def select_active_model(selection: ModelSelection):
    select_model(selection.model_id)
    return model_status()


@app.post("/api/model/download")
def start_model_download():
    status = model_status()
    if status.available:
        return status
    if status.download_state == "downloading":
        return status
    executor.submit(download_model, status.selected_model)
    return model_status()


@app.post("/api/model/download/cancel")
def cancel_model_download():
    request_model_download_cancel()
    return model_status()


@app.get("/api/ollama/status", response_model=OllamaServiceStatus)
def get_ollama_status() -> OllamaServiceStatus:
    return ollama_status()


@app.post("/api/ollama/models/pull", response_model=OllamaPullStatus)
def start_ollama_model_pull(request: OllamaPullRequest) -> OllamaPullStatus:
    current = ollama_pull_status(request.model_id)
    if current.state == "downloading":
        return current
    if check_ollama_model(request.model_id).available:
        return OllamaPullStatus(
            model_id=request.model_id,
            state="completed",
            progress=100,
            progress_label="模型已就绪",
            message=f"已检测到 {request.model_id}",
        )
    ollama_executor.submit(pull_ollama_model, request.model_id)
    return ollama_pull_status(request.model_id)


@app.get("/api/ollama/models/{model_id:path}/pull", response_model=OllamaPullStatus)
def get_ollama_model_pull_status(model_id: str) -> OllamaPullStatus:
    return ollama_pull_status(model_id)


@app.post("/api/ollama/models/pull/cancel", response_model=OllamaPullStatus)
def cancel_ollama_model_pull(request: OllamaPullRequest) -> OllamaPullStatus:
    return request_ollama_pull_cancel(request.model_id)


@app.get("/api/ollama/preflight", response_model=OllamaPreflightStatus)
def get_ollama_preflight(model_id: str, task: str) -> OllamaPreflightStatus:
    return ollama_preflight(model_id, task)


@app.get("/api/ollama/models/{model_id:path}", response_model=OllamaModelCheck)
def get_ollama_model_status(model_id: str) -> OllamaModelCheck:
    return check_ollama_model(model_id)


@app.post("/api/jobs", response_model=JobStatus)
async def create_job(
    file: UploadFile | None = File(default=None),
    source_url: str | None = Form(default=None),
    language: str = Form(default="auto"),
    formats: str = Form(default="txt"),
    include_timestamps: bool = Form(default=True),
    start_time: str | None = Form(default=None),
    end_time: str | None = Form(default=None),
    transcription_engine: TranscriptionEngine = Form(default=TranscriptionEngine.whisper),
    whisper_model_id: str | None = Form(default=None),
    transcription_model_id: str | None = Form(default=None),
    enable_polish: bool = Form(default=False),
    polish_model_id: str | None = Form(default=None),
) -> JobStatus:
    has_file = bool(file and file.filename)
    try:
        clean_source_url = normalize_source_url(source_url) if source_url else None
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not has_file and not clean_source_url:
        raise HTTPException(status_code=400, detail="请上传本地文件或填写视频链接")

    try:
        parsed_formats = parse_formats(formats)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    active_transcription_engine = TranscriptionEngine(transcription_engine)
    active_whisper_model_id = settings.model_definition(whisper_model_id or current_model_id()).id
    active_transcription_model_id = (
        settings.ollama_transcription_model_definition(transcription_model_id).id
        if active_transcription_engine == TranscriptionEngine.ollama_audio
        else None
    )
    active_polish_model_id = settings.ollama_polish_model_definition(polish_model_id).id if enable_polish else None

    if active_transcription_engine == TranscriptionEngine.ollama_audio:
        check = check_ollama_model(active_transcription_model_id or settings.default_ollama_transcription_model_id)
        if not check.service_available:
            raise HTTPException(status_code=503, detail="Ollama 服务不可用，请先启动 Ollama。")
        if not check.available:
            raise HTTPException(status_code=409, detail=f"未检测到 {check.model_id}，请先下载模型")

    if enable_polish and active_polish_model_id:
        check = check_ollama_model(active_polish_model_id)
        if not check.service_available:
            raise HTTPException(status_code=503, detail="Ollama 服务不可用，请先启动 Ollama。")
        if not check.available:
            raise HTTPException(status_code=409, detail=f"未检测到 {check.model_id}，请先下载模型")

    job_id = uuid4().hex
    work_dir = settings.jobs_dir / job_id
    work_dir.mkdir(parents=True, exist_ok=True)
    source_path: Path | None = None
    base_name = "transcript"
    source_label = clean_source_url or "本地文件"

    if has_file and file is not None:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in SUPPORTED_UPLOAD_SUFFIXES:
            raise HTTPException(status_code=400, detail=f"暂不支持该文件格式: {suffix or '未知'}")
        base_name = safe_stem(file.filename or "upload")
        source_label = file.filename or "本地文件"
        source_path = work_dir / f"source{suffix}"
        with source_path.open("wb") as handle:
            shutil.copyfileobj(file.file, handle)
    elif clean_source_url:
        base_name = safe_stem(clean_source_url)

    model_id = active_whisper_model_id
    if active_transcription_engine == TranscriptionEngine.ollama_audio:
        planned_label = f"{active_transcription_model_id}（Ollama direct audio，实验性）"
    elif enable_polish and active_polish_model_id:
        planned_label = f"{planned_model_label(model_id)} + {active_polish_model_id} polish"
    else:
        planned_label = planned_model_label(model_id)
    job = job_store.create(
        job_id,
        work_dir,
        source_label,
        clean_source_url,
        language,
        start_time,
        end_time,
        model_id,
        planned_label,
        parsed_formats,
        include_timestamps,
        active_transcription_engine,
        active_whisper_model_id if active_transcription_engine == TranscriptionEngine.whisper else None,
        active_transcription_model_id,
        enable_polish,
        active_polish_model_id,
    )
    add_event(job_id, "job created")
    add_event(job_id, "model check started")
    checked_models = [active_transcription_model_id] if active_transcription_engine == TranscriptionEngine.ollama_audio else [model_id]
    if enable_polish and active_polish_model_id:
        checked_models.append(active_polish_model_id)
    add_event(job_id, f"model check completed: {', '.join(model for model in checked_models if model)}")
    executor.submit(
        run_job,
        job_id,
        source_path,
        clean_source_url,
        base_name,
        language,
        parsed_formats,
        include_timestamps,
        start_time,
        end_time,
        model_id,
        active_transcription_engine,
        active_transcription_model_id,
        enable_polish,
        active_polish_model_id,
    )
    return build_status(job)


@app.get("/api/jobs", response_model=list[JobStatus])
def list_jobs() -> list[JobStatus]:
    return [build_status(job) for job in job_store.list()]


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return build_status(job)


@app.post("/api/jobs/{job_id}/cancel", response_model=JobStatus)
def cancel_job(job_id: str) -> JobStatus:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if job.state in {JobState.completed, JobState.failed, JobState.canceled}:
        return build_status(job)
    return build_status(job_store.request_cancel(job_id))


@app.get("/api/jobs/{job_id}/download/{filename}")
def download_output(job_id: str, filename: str) -> FileResponse:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    path = job.work_dir / Path(filename).name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在或已被删除")
    return FileResponse(path, filename=path.name)


@app.delete("/api/jobs/{job_id}/outputs/{filename}", response_model=JobStatus)
def delete_output(job_id: str, filename: str) -> JobStatus:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    safe_name = Path(filename).name
    path = job.work_dir / safe_name
    if path.exists() and path.is_file():
        unlink_file(path)
    remaining_outputs = [output for output in job.outputs if output.name != safe_name]
    updated = job_store.update(job_id, outputs=remaining_outputs)
    return build_status(updated)


static_dir = ROOT_DIR / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
