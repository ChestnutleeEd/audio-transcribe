from __future__ import annotations

import shutil
import platform
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import Body, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.schemas import (
    AppOptions,
    ErrorDiagnostic,
    ExportScope,
    HealthCheckStatus,
    JobWorkFileCleanupStatus,
    JobState,
    JobStatus,
    LocalModelDetectionStatus,
    MLXWhisperStatus,
    AudioModelTestRequest,
    AudioModelTestResult,
    CustomModelRegistration,
    ModelCapabilities,
    ModelRegistryStatus,
    ModelSelection,
    WhisperModelPathBinding,
    OllamaModelCheck,
    OllamaPreflightStatus,
    OllamaPullRequest,
    OllamaPullStatus,
    OllamaServiceStatus,
    OptionItem,
    OutputFile,
    OutputFormat,
    PolishProfile,
    PolishRequest,
    QwenAudioStatus,
    UnifiedModel,
    TranscriptionEngine,
)
from app.services.audio_engine import AudioEngineResult
from app.services.audio_engines import QwenAudioEngine
from app.services.exporters import TranscriptSegment, export_transcript, segment_text
from app.services.health import health_check
from app.services.local_model_detection import detect_local_models
from app.services.model_registry import (
    custom_path_or_id_exists,
    custom_path_or_id_is_path_like,
    delete_custom_model,
    model_registry,
    probe_custom_model,
    register_custom_model,
    test_audio_model,
)
from app.services.mlx_whisper_provider import mlx_whisper_status, transcribe_with_mlx_whisper
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
    bind_model_path,
    current_model_id,
    download_model,
    model_status,
    request_model_download_cancel,
    select_model,
    set_runtime_device,
    unbind_model_path,
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
from app.services.ollama_provider import transcribe_audio_direct
from app.services.polish_router import polish_segments, resolve_polish_model, validate_polish_model
from app.services.qwen_audio import qwen_audio_status
from app.services.polish_profiles import combine_instruction, get_profile, profile_options
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


def parse_export_scope(value: str | None) -> ExportScope:
    try:
        return ExportScope(value or ExportScope.raw.value)
    except ValueError:
        return ExportScope.raw


def unlink_file(path: Path) -> None:
    if path.exists() and path.is_file():
        path.unlink()


def is_path_inside(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def known_active_work_dirs() -> set[Path]:
    return {
        job.work_dir.resolve()
        for job in job_store.list()
        if job.work_dir is not None and not terminal_state(job.state)
    }


def eligible_work_dirs() -> tuple[list[Path], int, list[str]]:
    jobs_dir = settings.jobs_dir.resolve()
    active_dirs = known_active_work_dirs()
    skipped: list[str] = []
    eligible: list[Path] = []
    if not jobs_dir.exists():
        return eligible, 0, skipped

    for child in sorted(jobs_dir.iterdir(), key=lambda item: item.name):
        if not child.is_dir() or child.is_symlink():
            continue
        resolved = child.resolve()
        if not is_path_inside(resolved, jobs_dir):
            skipped.append(f"跳过 jobs 目录外路径：{child}")
            continue
        if resolved in active_dirs:
            continue
        eligible.append(child)
    return eligible, len(active_dirs), skipped


def collect_work_files(work_dirs: list[Path]) -> tuple[list[Path], int, list[str]]:
    jobs_dir = settings.jobs_dir.resolve()
    files: list[Path] = []
    total_bytes = 0
    skipped: list[str] = []
    for work_dir in work_dirs:
        for path in work_dir.rglob("*"):
            if not is_path_inside(path, jobs_dir):
                skipped.append(f"跳过 jobs 目录外路径：{path}")
                continue
            if path.is_dir() and not path.is_symlink():
                continue
            if not path.exists():
                continue
            try:
                total_bytes += path.stat().st_size
            except OSError as exc:
                skipped.append(f"无法读取文件大小：{path.name}，原因：{exc}")
                continue
            files.append(path)
    return files, total_bytes, skipped


def cleanup_status() -> JobWorkFileCleanupStatus:
    work_dirs, active_jobs, skipped_dirs = eligible_work_dirs()
    files, total_bytes, skipped_files = collect_work_files(work_dirs)
    return JobWorkFileCleanupStatus(
        jobs_dir=str(settings.jobs_dir),
        eligible_jobs=len(work_dirs),
        active_jobs=active_jobs,
        files=len(files),
        bytes=total_bytes,
        skipped=[*skipped_dirs, *skipped_files],
    )


def cleanup_work_files() -> JobWorkFileCleanupStatus:
    work_dirs, active_jobs, skipped_dirs = eligible_work_dirs()
    files, _, skipped_files = collect_work_files(work_dirs)
    cleaned_files = 0
    cleaned_bytes = 0
    skipped = [*skipped_dirs, *skipped_files]

    for path in files:
        if not path.exists():
            continue
        try:
            size = path.stat().st_size
            path.unlink()
            cleaned_files += 1
            cleaned_bytes += size
        except OSError as exc:
            skipped.append(f"删除失败：{path.name}，原因：{exc}")

    cleaned_jobs = 0
    for work_dir in work_dirs:
        directories = [path for path in work_dir.rglob("*") if path.is_dir() and not path.is_symlink()]
        for directory in sorted(directories, key=lambda item: len(item.parts), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass
        try:
            work_dir.rmdir()
            cleaned_jobs += 1
        except OSError:
            pass

    cleaned_work_dirs = {work_dir.resolve() for work_dir in work_dirs}
    for job in job_store.list():
        if job.work_dir is not None and job.work_dir.resolve() in cleaned_work_dirs:
            job_store.update(job.id, outputs=[])

    return JobWorkFileCleanupStatus(
        jobs_dir=str(settings.jobs_dir),
        eligible_jobs=len(work_dirs),
        active_jobs=active_jobs,
        files=len(files),
        bytes=cleaned_bytes,
        cleaned_jobs=cleaned_jobs,
        cleaned_files=cleaned_files,
        cleaned_bytes=cleaned_bytes,
        skipped=skipped,
    )


def build_status(job: Job) -> JobStatus:
    status_segments = [
        {
            "id": index,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        }
        for index, segment in enumerate(job.raw_segments, start=1)
    ]
    metadata = {
        "engine": job.transcription_engine.value,
        "engineName": job.transcription_engine.value,
        "modelLabel": job.model_label,
        "transcriptionModel": job.whisper_model_id or job.transcription_model_id or job.model_id,
        "durationSeconds": job.duration_seconds,
        **job.engine_metadata,
    }
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
        polish_profile_id=job.polish_profile_id,
        polish_profile_label=job.polish_profile_label,
        polish_custom_instruction=job.polish_custom_instruction,
        model_label=job.model_label,
        formats=job.formats,
        export_scope=job.export_scope,
        include_timestamps=job.include_timestamps,
        created_at=job.created_at,
        outputs=job.outputs,
        warnings=job.warnings,
        events=job.events,
        error=job.error,
        error_diagnostic=job.error_diagnostic,
        raw_text=job.raw_text,
        rawText=job.raw_text,
        segments=status_segments,
        metadata=metadata,
        engine_name=job.transcription_engine.value,
        polished_text=job.polished_text,
        has_segments=bool(job.raw_segments),
        duration_seconds=job.duration_seconds,
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


def resolve_polish_model_id(model_id: str | None) -> str:
    candidate = (model_id or "").strip()
    if not candidate:
        return ""
    return candidate


def terminal_state(state: JobState) -> bool:
    return state in {JobState.completed, JobState.failed, JobState.cancelled}


def diagnose_error(error: str, context: str | None = None) -> ErrorDiagnostic:
    text = (error or "").strip()
    lower = text.lower()
    if "ollama 服务不可用" in text or "connection refused" in lower:
        return ErrorDiagnostic(
            code="OLLAMA_NOT_RUNNING",
            title="Ollama 未运行",
            message="本地 Ollama 服务不可用，文本整理或音频直转无法继续。",
            action="启动 Ollama 桌面应用，或在终端执行 ollama serve 后重试。",
            technical_detail=text,
        )
    if "未检测到" in text and ("gemma" in lower or "ollama" in lower):
        return ErrorDiagnostic(
            code="OLLAMA_MODEL_MISSING",
            title="Ollama 模型缺失",
            message="所选 Ollama 模型不在本地模型列表中。",
            action="切换到已安装模型；如需新增模型，请在应用外手动安装。",
            technical_detail=text,
        )
    if "ffmpeg" in lower:
        return ErrorDiagnostic(
            code="FFMPEG_MISSING",
            title="FFmpeg 不可用",
            message="音频预处理失败，通常是 FFmpeg 未安装或路径不可用。",
            action="安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。",
            technical_detail=text,
        )
    if "mlx whisper" in lower or "mlx-whisper" in lower or "mlx_whisper" in lower:
        return ErrorDiagnostic(
            code="MLX_WHISPER_UNAVAILABLE",
            title="MLX Whisper 不可用",
            message="MLX Whisper 转录前置条件未满足。",
            action="确认当前是 Apple Silicon Mac、已自行安装 mlx-whisper，并配置本地 MLX 模型目录或已缓存 repo id。",
            technical_detail=text,
        )
    if "qwen2-audio" in lower or "qwen-audio" in lower or "mlx-audio" in lower:
        return ErrorDiagnostic(
            code="QWEN_AUDIO_UNAVAILABLE",
            title="Qwen2-Audio 不可用",
            message="Qwen2-Audio 多模态音频理解前置条件未满足。",
            action="确认当前是 Apple Silicon Mac、已自行安装 mlx-audio，并配置本地 Qwen2-Audio 模型目录或已缓存 repo id。",
            technical_detail=text,
        )
    if "未检测到模型" in text or "model.bin" in lower:
        return ErrorDiagnostic(
            code="WHISPER_MODEL_MISSING",
            title="Whisper 模型缺失",
            message="当前 faster-whisper 模型文件不完整或未下载。",
            action="在页面选择模型并确认下载，或手动把模型文件放入 models/ 对应目录。",
            technical_detail=text,
        )
    if "文件格式" in text or "invalid data" in lower or "音频预处理失败" in text:
        return ErrorDiagnostic(
            code="INVALID_AUDIO_FILE",
            title="音频文件不可处理",
            message="上传文件可能损坏、格式不支持，或无法被 FFmpeg 解码。",
            action="换一个音频文件，或先用 FFmpeg/播放器确认文件可正常播放。",
            technical_detail=text,
        )
    if "超时" in text or "timeout" in lower:
        return ErrorDiagnostic(
            code="TRANSCRIBE_TIMEOUT",
            title="处理超时",
            message="下载、转录或模型调用耗时过长。",
            action="检查网络和模型运行状态，或先截取较短音频重试。",
            technical_detail=text,
        )
    if "text 为空" in text or "不包含 json" in text or "返回内容" in text:
        return ErrorDiagnostic(
            code="POLISH_EMPTY_RESPONSE",
            title="文本整理返回内容不可用",
            message="Ollama 返回为空、不是 JSON，或不符合 segments 结构。",
            action="切换到保守清理配置或 gemma3:1b 后重新整理。",
            technical_detail=text,
        )
    if context == "cancelled" or "任务已停止" in text:
        return ErrorDiagnostic(
            code="TASK_CANCELLED",
            title="任务已取消",
            message="当前任务已停止，后续结果会被忽略。",
            action="需要时重新提交任务。",
            technical_detail=text,
        )
    return ErrorDiagnostic(
        code="UNKNOWN_ERROR",
        title="任务失败",
        message="任务执行过程中发生未分类错误。",
        action="查看技术细节，确认环境检查通过后重试。",
        technical_detail=text,
    )


def ensure_not_cancelled(job_id: str) -> None:
    if is_job_canceled(job_id):
        raise OperationCanceled("任务已停止")


def export_metadata(job: Job) -> dict[str, object]:
    return {
        "engine": job.transcription_engine.value,
        "language": job.language,
        "transcriptionModel": job.whisper_model_id or job.transcription_model_id or job.model_id,
        "modelLabel": job.model_label,
        "enablePolish": job.enable_polish,
        "polishModel": job.polish_model_id,
        "polishProfile": job.polish_profile_label,
        "source": job.source_label,
        "durationSeconds": job.duration_seconds,
        **job.engine_metadata,
    }


def build_output_files(job_id: str, paths: list[Path]) -> list[OutputFile]:
    return [
        OutputFile(
            name=path.name,
            format=OutputFormat(path.suffix.lstrip(".")),
            bytes=path.stat().st_size,
            download_url=f"/api/jobs/{job_id}/download/{path.name}",
        )
        for path in paths
    ]


def regenerate_exports(job_id: str) -> list[OutputFile]:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        return []
    output_paths = export_transcript(
        job.work_dir,
        job.base_name,
        job.formats,
        job.raw_segments,
        job.polished_segments or None,
        job.include_timestamps,
        job.export_scope,
        export_metadata(job),
    )
    return build_output_files(job_id, output_paths)


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
    polish_profile_id: str | None,
    polish_custom_instruction: str | None,
    export_scope: ExportScope,
) -> None:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        return

    try:
        job_store.update(job_id, processing_started_at=utc_now_iso(), processing_finished_at=None)
        add_event(job_id, "任务开始")
        if job.cancel_requested:
            job_store.update(
                job_id,
                state=JobState.cancelled,
                progress=100,
                message="已取消排队任务",
                error_diagnostic=diagnose_error("已取消排队任务", "cancelled"),
                processing_finished_at=utc_now_iso(),
            )
            return

        job_store.update(job_id, state=JobState.validating, progress=8, message="准备音频来源")
        work_dir = job.work_dir
        media_path = source_path
        if media_path is None and source_url:
            if settings.mock_mode:
                add_event(job_id, "Mock 模式：跳过来源下载")
                media_path = work_dir / "mock_source.wav"
            else:
                media_path = download_audio(source_url, work_dir, lambda: is_job_canceled(job_id))
                base_name = safe_stem(media_path.name)
                job_store.update(job_id, source_label=Path(media_path).stem)

        if media_path is None:
            raise ValueError("缺少上传文件或视频链接")

        ensure_not_cancelled(job_id)

        job_store.update(job_id, state=JobState.preparing_model, progress=24, message="准备 16k 单声道音频")
        wav_path = work_dir / "input_16k.wav"
        if settings.mock_mode:
            add_event(job_id, "Mock 模式：跳过音频标准化")
        else:
            normalize_audio(media_path, wav_path, start_time, end_time, lambda: is_job_canceled(job_id))

        if transcription_engine == TranscriptionEngine.whisper:
            job_store.update(job_id, state=JobState.preparing_model, progress=42, message=f"加载 {model_id} 模型")
            add_event(job_id, "Whisper 转录开始")

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
                        state=JobState.transcribing,
                        progress=50,
                        message="模型已加载，开始转写",
                        model_label=label,
                    )
                elif stage == "transcribing":
                    label = loaded_model_label(model_meta)
                    job_store.update(
                        job_id,
                        state=JobState.transcribing,
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
                        state=JobState.transcribing,
                        progress=52,
                        message="CUDA 转写进程异常退出，正在切换 CPU 重试",
                        model_label=label,
                    )

            try:
                if settings.mock_mode:
                    segments = mock_whisper_segments()
                    job_store.update(
                        job_id,
                        state=JobState.transcribing,
                        progress=58,
                        message="Mock Whisper 转录完成",
                        model_label=f"{model_id}（mock）",
                    )
                else:
                    segments = transcribe_audio(
                        wav_path,
                        language,
                        lambda: is_job_canceled(job_id),
                        update_transcribe_status,
                        model_id,
                    )
                add_event(job_id, "Whisper 转录完成")
            except Exception as exc:
                add_event(job_id, f"Whisper 转录失败：{exc}", "error")
                raise
        elif transcription_engine == TranscriptionEngine.mlx_whisper:
            active_mlx_model = (transcription_model_id or settings.mlx_whisper_model_path_or_repo).strip()
            job_store.update(
                job_id,
                state=JobState.transcribing,
                progress=50,
                message="正在使用 MLX Whisper 转录音频",
                model_label=f"{active_mlx_model or settings.mlx_whisper_default_model_label}（MLX Whisper）",
            )
            add_event(job_id, "MLX Whisper 转录开始")
            try:
                if settings.mock_mode:
                    segments = mock_whisper_segments()
                    job_store.update(
                        job_id,
                        state=JobState.transcribing,
                        progress=58,
                        message="Mock MLX Whisper 转录完成",
                        model_label=f"{active_mlx_model or settings.mlx_whisper_default_model_label}（MLX mock）",
                    )
                else:
                    segments = transcribe_with_mlx_whisper(wav_path, active_mlx_model, language)
                add_event(job_id, "MLX Whisper 转录完成")
            except Exception as exc:
                unlink_file(wav_path)
                add_event(job_id, f"MLX Whisper 转录失败：{exc}", "error")
                job_store.update(
                    job_id,
                    state=JobState.failed,
                    progress=100,
                    message=f"MLX Whisper 转录失败：{exc}",
                    error=str(exc),
                    error_diagnostic=diagnose_error(str(exc)),
                    processing_finished_at=utc_now_iso(),
                )
                return
        elif transcription_engine == TranscriptionEngine.qwen_audio:
            active_qwen_model = (transcription_model_id or settings.qwen_audio_model_path_or_repo).strip()
            job_store.update(
                job_id,
                state=JobState.transcribing,
                progress=48,
                message="正在使用 Qwen2-Audio 切分音频并准备流式理解",
                model_label=f"{settings.qwen_audio_default_model_label}（MLX Audio）",
                engine_metadata={
                    "engine": "qwen-audio",
                    "backend": "mlx-audio",
                    "model": settings.qwen_audio_default_model_label,
                    "modelPathOrRepo": active_qwen_model,
                    "partial_results": [],
                },
            )
            add_event(job_id, "Qwen2-Audio 多模态音频理解开始")

            def update_qwen_partial(result: AudioEngineResult) -> None:
                if is_job_canceled(job_id):
                    return
                partial_count = len(result.metadata.get("partial_results") or [])
                progress = min(72, 50 + partial_count * 4)
                job_store.update(
                    job_id,
                    state=JobState.transcribing,
                    progress=progress,
                    message=f"Qwen2-Audio 已完成 {partial_count} 个音频 chunk",
                    raw_segments=result.segments,
                    raw_text=result.raw_text,
                    duration_seconds=max((segment.end for segment in result.segments), default=None),
                    engine_metadata=result.metadata,
                    model_label=result.model_label,
                )

            try:
                if settings.mock_mode:
                    segments = [
                        TranscriptSegment(start=0.0, end=15.0, text="这是 mock Qwen2-Audio 音频理解的第一段。"),
                        TranscriptSegment(start=15.0, end=30.0, text="这是 mock Qwen2-Audio 音频理解的第二段，用于验证 chunk 级 streaming。"),
                    ]
                    job_store.update(
                        job_id,
                        state=JobState.transcribing,
                        progress=58,
                        message="Mock Qwen2-Audio 音频理解完成",
                        model_label=f"{settings.qwen_audio_default_model_label}（MLX mock）",
                        raw_segments=segments,
                        raw_text=segment_text(segments, include_timestamps=False),
                        duration_seconds=max((segment.end for segment in segments), default=None),
                        engine_metadata={
                            "engine": "qwen-audio",
                            "backend": "mlx-audio",
                            "model": settings.qwen_audio_default_model_label,
                            "modelPathOrRepo": active_qwen_model,
                            "partial_results": [
                                {"start": 0.0, "end": 15.0, "text": segments[0].text, "chunk_id": 1},
                                {"start": 15.0, "end": 30.0, "text": segments[1].text, "chunk_id": 2},
                            ],
                            "finalJson": {
                                "segments": [
                                    {"start": 0.0, "end": 15.0, "text": segments[0].text, "chunk_id": 1},
                                    {"start": 15.0, "end": 30.0, "text": segments[1].text, "chunk_id": 2},
                                ],
                                "full_text": segment_text(segments, include_timestamps=False),
                            },
                        },
                    )
                else:
                    qwen_engine = QwenAudioEngine(model_path_or_repo=active_qwen_model, work_dir=work_dir)
                    qwen_result = qwen_engine.transcribe(
                        wav_path,
                        language,
                        lambda: is_job_canceled(job_id),
                        update_qwen_partial,
                    )
                    segments = qwen_result.segments
                    job_store.update(
                        job_id,
                        model_label=qwen_result.model_label,
                        engine_metadata=qwen_result.metadata,
                    )
                add_event(job_id, "Qwen2-Audio 多模态音频理解完成")
            except Exception as exc:
                unlink_file(wav_path)
                add_event(job_id, f"Qwen2-Audio 多模态音频理解失败：{exc}", "error")
                job_store.update(
                    job_id,
                    state=JobState.failed,
                    progress=100,
                    message=f"Qwen2-Audio 多模态音频理解失败：{exc}",
                    error=str(exc),
                    error_diagnostic=diagnose_error(str(exc)),
                    processing_finished_at=utc_now_iso(),
                )
                return
        elif transcription_engine == TranscriptionEngine.ollama_audio:
            active_transcription_model = transcription_model_id or settings.default_ollama_transcription_model_id
            job_store.update(
                job_id,
                state=JobState.transcribing,
                progress=50,
                message=f"正在使用本地大模型音频转录：{active_transcription_model}",
                model_label=f"{active_transcription_model}（本地大模型音频转录，实验性）",
            )
            add_event(job_id, "本地大模型音频转录开始")
            try:
                direct_result = transcribe_audio_direct(wav_path, active_transcription_model)
            except OllamaError as exc:
                unlink_file(wav_path)
                add_event(job_id, f"本地大模型音频转录失败：{exc}", "error")
                job_store.update(
                    job_id,
                    state=JobState.failed,
                    progress=100,
                    message=f"本地大模型音频转录失败：{exc}",
                    error=str(exc),
                    error_diagnostic=diagnose_error(str(exc)),
                    processing_finished_at=utc_now_iso(),
                )
                return
            segments = direct_result.segments
            add_event(job_id, "本地大模型音频转录完成")
            for warning in direct_result.warnings:
                append_job_warning(job_id, warning)
        else:
            raise ValueError(f"不支持的转录引擎: {transcription_engine}")

        if not segments:
            raise RuntimeError("没有识别到可用文本")

        ensure_not_cancelled(job_id)

        raw_segments = offset_segments(segments, parse_time_offset(start_time))
        engine_metadata = dict(job_store.get(job_id).engine_metadata if job_store.get(job_id) else {})
        if transcription_engine == TranscriptionEngine.qwen_audio and isinstance(engine_metadata.get("finalJson"), dict):
            final_json = dict(engine_metadata["finalJson"])
            final_json["segments"] = [
                {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text,
                    "chunk_id": index,
                }
                for index, segment in enumerate(raw_segments, start=1)
            ]
            final_json["full_text"] = segment_text(raw_segments, include_timestamps=False)
            engine_metadata["finalJson"] = final_json
        job_store.update(
            job_id,
            raw_segments=raw_segments,
            raw_text=segment_text(raw_segments, include_timestamps=False),
            duration_seconds=max((segment.end for segment in raw_segments), default=None),
            engine_metadata=engine_metadata,
        )

        polished_segments: list[TranscriptSegment] | None = None
        if enable_polish:
            active_polish_model_ref = resolve_polish_model(polish_model_id or settings.default_ollama_polish_model_id)
            if active_polish_model_ref is None:
                raise RuntimeError("请选择文本整理模型")
            active_polish_model = active_polish_model_ref.path_or_id
            profile = get_profile(polish_profile_id)
            profile_instruction = combine_instruction(profile, polish_custom_instruction)
            job_store.update(
                job_id,
                state=JobState.polishing,
                progress=74,
                message=f"正在使用 {active_polish_model} 执行 {profile.label}",
                polish_profile_id=profile.id,
                polish_profile_label=profile.label,
                polish_custom_instruction=(polish_custom_instruction or "").strip() or None,
            )
            add_event(job_id, "文本整理开始")
            try:
                polish_result = polish_segments(
                    raw_segments,
                    active_polish_model_ref,
                    profile_instruction,
                    on_event=lambda message, level="info": add_event(job_id, message, level),
                    on_warning=lambda warning: append_job_warning(job_id, warning),
                )
                polished_segments = polish_result.segments if polish_result.success_batches else None
                job_store.update(
                    job_id,
                    polished_segments=polished_segments or [],
                    polished_text=segment_text(polished_segments, include_timestamps=False) if polished_segments else None,
                )
                if polish_result.failed_batches:
                    job_store.update(
                        job_id,
                        progress=80,
                        message=(
                            "文本整理部分完成，失败批次已保留原始转录结果"
                            if polish_result.success_batches
                            else "文本整理失败，已保留原始转录结果"
                        ),
                    )
                else:
                    job_store.update(job_id, progress=80, message="文本整理完成")
            except Exception as exc:
                warning = f"文本整理失败，已保留原始转录结果：{exc}"
                append_job_warning(job_id, warning)
                add_event(job_id, warning, "warning")
                polished_segments = None
                job_store.update(job_id, polished_segments=[], polished_text=None, progress=80, message=warning)

        ensure_not_cancelled(job_id)
        job_store.update(job_id, progress=82, message="生成转录文件")
        actual_export_scope = export_scope
        if export_scope == ExportScope.polished and not polished_segments:
            actual_export_scope = ExportScope.raw
            append_job_warning(job_id, "整理后的转录结果不可用，本次导出已安全降级为原始转录结果。")
        output_paths = export_transcript(
            work_dir,
            base_name,
            formats,
            raw_segments,
            polished_segments,
            include_timestamps,
            actual_export_scope,
            export_metadata(job_store.get(job_id) or job),
        )
        add_event(job_id, "导出文件已生成")
        outputs = build_output_files(job_id, output_paths)

        ensure_not_cancelled(job_id)

        for temporary in [wav_path]:
            unlink_file(temporary)

        job_store.update(
            job_id,
            state=JobState.completed,
            progress=100,
            message="转录完成，可下载、复制或重新执行文本整理",
            outputs=outputs,
            processing_finished_at=utc_now_iso(),
        )
    except OperationCanceled as exc:
        add_event(job_id, str(exc), "warning")
        job_store.update(
            job_id,
            state=JobState.cancelled,
            progress=100,
            message=str(exc),
            error=None,
            error_diagnostic=diagnose_error(str(exc), "cancelled"),
            processing_finished_at=utc_now_iso(),
        )
    except Exception as exc:
        add_event(job_id, f"任务失败：{exc}", "error")
        job_store.update(
            job_id,
            state=JobState.failed,
            progress=100,
            message="任务失败",
            error=str(exc),
            error_diagnostic=diagnose_error(str(exc)),
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
            OptionItem(value="json", label="JSON"),
            OptionItem(value="srt", label="SRT"),
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


@app.get("/api/models/registry", response_model=ModelRegistryStatus)
def get_model_registry() -> ModelRegistryStatus:
    return model_registry()


@app.post("/api/models/probe", response_model=UnifiedModel)
def probe_model(request: CustomModelRegistration) -> UnifiedModel:
    path_or_id = request.path_or_id.strip()
    if not path_or_id:
        raise HTTPException(status_code=400, detail="请填写模型路径或模型 ID")
    return probe_custom_model(request)


@app.api_route("/api/models/register", methods=["GET", "POST"], response_model=UnifiedModel)
def register_model(
    http_request: Request,
    request: CustomModelRegistration | None = Body(default=None),
    provider: str = Query(default="custom"),
    path_or_id: str = Query(default=""),
    audio: bool = Query(default=False),
    text: bool = Query(default=False),
) -> UnifiedModel:
    if http_request.method == "GET":
        request = CustomModelRegistration(
            provider=provider,  # type: ignore[arg-type]
            path_or_id=path_or_id,
            capabilities=ModelCapabilities(audio=audio, text=text),
        )
    if request is None:
        raise HTTPException(status_code=400, detail="请使用 JSON body 或 query 参数提交模型注册信息")
    path_or_id = request.path_or_id.strip()
    if not path_or_id:
        raise HTTPException(status_code=400, detail="请填写模型路径或模型 ID")
    if request.provider in {"custom", "mlx", "huggingface"} and not custom_path_or_id_is_path_like(path_or_id):
        raise HTTPException(status_code=400, detail="请填写完整本地模型目录路径")
    if custom_path_or_id_is_path_like(path_or_id) and not custom_path_or_id_exists(path_or_id):
        raise HTTPException(status_code=400, detail=f"模型路径不存在：{path_or_id}")
    return register_custom_model(request)


@app.delete("/api/models/register")
def unregister_model(
    provider: str = Query(default="custom"),
    path_or_id: str = Query(default=""),
) -> dict[str, bool]:
    if not path_or_id.strip():
        raise HTTPException(status_code=400, detail="请提供要删除的模型路径")
    deleted = delete_custom_model(provider, path_or_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="未找到该绑定模型")
    return {"deleted": True}


@app.api_route("/api/models/pick-directory", methods=["GET", "POST"])
def pick_model_directory():
    if platform.system().lower() == "darwin":
        script = 'POSIX path of (choose folder with prompt "选择模型文件夹")'
        try:
            result = subprocess.run(
                ["osascript", "-e", script],
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"打开 macOS 文件夹选择器失败：{exc}") from exc
        if result.returncode == 0 and result.stdout.strip():
            return {"path": result.stdout.strip().rstrip("/")}
        message = (result.stderr or "").strip()
        if "User canceled" in message or result.returncode == 1:
            raise HTTPException(status_code=400, detail="未选择文件夹")
        raise HTTPException(status_code=500, detail=f"打开 macOS 文件夹选择器失败：{message or result.returncode}")

    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"当前 Python 环境无法打开系统文件夹选择器：{exc}") from exc

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        selected = filedialog.askdirectory(title="选择模型文件夹")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"打开系统文件夹选择器失败：{exc}") from exc
    finally:
        if root is not None:
            root.destroy()

    if not selected:
        raise HTTPException(status_code=400, detail="未选择文件夹")
    return {"path": selected}


@app.post("/api/models/audio-test", response_model=AudioModelTestResult)
def quick_test_audio_model(request: AudioModelTestRequest) -> AudioModelTestResult:
    return test_audio_model(request)


@app.post("/api/model/select")
def select_active_model(selection: ModelSelection):
    select_model(selection.model_id)
    return model_status()


@app.post("/api/model/path")
def bind_active_model_path(binding: WhisperModelPathBinding):
    try:
        bind_model_path(binding.model_id, binding.path)
        select_model(binding.model_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return model_status()


@app.delete("/api/model/path/{model_id}")
def unbind_active_model_path(model_id: str):
    unbind_model_path(model_id)
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


@app.get("/api/polish/profiles", response_model=list[PolishProfile])
def get_polish_profiles() -> list[PolishProfile]:
    return profile_options()


@app.get("/api/local-models/detect", response_model=LocalModelDetectionStatus)
def get_local_model_detection() -> LocalModelDetectionStatus:
    return detect_local_models()


@app.get("/api/mlx-whisper/status", response_model=MLXWhisperStatus)
def get_mlx_whisper_status(model_path_or_repo: str | None = None) -> MLXWhisperStatus:
    return mlx_whisper_status(model_path_or_repo)


@app.get("/api/qwen-audio/status", response_model=QwenAudioStatus)
def get_qwen_audio_status(model_path_or_repo: str | None = None) -> QwenAudioStatus:
    return qwen_audio_status(model_path_or_repo)


@app.get("/api/health", response_model=HealthCheckStatus)
def get_health_check() -> HealthCheckStatus:
    return health_check()


@app.post("/api/jobs", response_model=JobStatus)
async def create_job(
    file: UploadFile | None = File(default=None),
    source_url: str | None = Form(default=None),
    language: str = Form(default="auto"),
    formats: str = Form(default="txt"),
    include_timestamps: bool = Form(default=True),
    start_time: str | None = Form(default=None),
    end_time: str | None = Form(default=None),
    transcription_engine: TranscriptionEngine = Form(default=TranscriptionEngine.qwen_audio),
    whisper_model_id: str | None = Form(default=None),
    transcription_model_id: str | None = Form(default=None),
    mlx_model_path_or_repo: str | None = Form(default=None),
    qwen_model_path_or_repo: str | None = Form(default=None),
    enable_polish: bool = Form(default=False),
    polish_model_id: str | None = Form(default=None),
    polish_profile_id: str | None = Form(default=None),
    polish_custom_instruction: str | None = Form(default=None),
    export_scope: str = Form(default=ExportScope.raw.value),
) -> JobStatus:
    if job_store.has_active_job():
        raise HTTPException(status_code=409, detail="已有任务正在处理。请先等待完成或取消当前任务。")

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
    active_export_scope = parse_export_scope(export_scope)
    if OutputFormat.srt in parsed_formats and not include_timestamps:
        parsed_formats = [fmt for fmt in parsed_formats if fmt != OutputFormat.srt]
    if not parsed_formats:
        raise HTTPException(status_code=400, detail="SRT 需要时间轴；请开启时间轴或选择 TXT / Markdown / JSON。")

    active_transcription_engine = TranscriptionEngine(transcription_engine)
    active_whisper_model_id = settings.model_definition(whisper_model_id or current_model_id()).id
    active_transcription_model_id: str | None = None
    if active_transcription_engine == TranscriptionEngine.ollama_audio:
        active_transcription_model_id = (transcription_model_id or "").strip()
        if not active_transcription_model_id:
            raise HTTPException(status_code=400, detail="请选择支持 Audio Input 的本地大模型")
    elif active_transcription_engine == TranscriptionEngine.mlx_whisper:
        active_transcription_model_id = (mlx_model_path_or_repo or settings.mlx_whisper_model_path_or_repo).strip()
    elif active_transcription_engine == TranscriptionEngine.qwen_audio:
        active_transcription_model_id = (qwen_model_path_or_repo or settings.qwen_audio_model_path_or_repo).strip()
    active_polish_model_ref = resolve_polish_model(polish_model_id) if enable_polish else None
    active_polish_model_id = active_polish_model_ref.path_or_id if active_polish_model_ref else None
    if enable_polish and not active_polish_model_ref:
        raise HTTPException(status_code=400, detail="请选择文本整理模型")
    active_profile = get_profile(polish_profile_id)

    if active_transcription_engine == TranscriptionEngine.ollama_audio:
        check = check_ollama_model(active_transcription_model_id or settings.default_ollama_transcription_model_id)
        if not check.service_available:
            raise HTTPException(status_code=503, detail="Ollama 服务不可用，请先启动 Ollama。")
        if not check.available:
            raise HTTPException(status_code=409, detail=f"未检测到 {check.model_id}，请先下载模型")
    elif active_transcription_engine == TranscriptionEngine.mlx_whisper:
        status = mlx_whisper_status(active_transcription_model_id)
        if not status.platform_supported:
            raise HTTPException(status_code=409, detail=status.reason or "MLX Whisper 当前平台不适配")
        if not status.dependency_installed:
            raise HTTPException(status_code=409, detail=status.reason or "未安装 mlx-whisper")
        if not status.model_configured:
            raise HTTPException(status_code=409, detail=status.reason or "未配置 MLX Whisper 模型")
        if not status.ffmpeg_available:
            raise HTTPException(status_code=409, detail=status.reason or "FFmpeg 不可用")
        if not status.available and status.reason:
            raise HTTPException(status_code=409, detail=status.reason)
    elif active_transcription_engine == TranscriptionEngine.qwen_audio and not settings.mock_mode:
        status = qwen_audio_status(active_transcription_model_id)
        if not status.platform_supported:
            raise HTTPException(status_code=409, detail=status.reason or "Qwen2-Audio 当前平台不适配")
        if not status.dependency_installed:
            raise HTTPException(status_code=409, detail=status.reason or "未安装 mlx-audio")
        if not status.model_configured:
            raise HTTPException(status_code=409, detail=status.reason or "未配置 Qwen2-Audio 模型")
        if not status.ffmpeg_available:
            raise HTTPException(status_code=409, detail=status.reason or "FFmpeg 不可用")
        if not status.available and status.reason:
            raise HTTPException(status_code=409, detail=status.reason)

    if enable_polish and active_polish_model_ref:
        try:
            validate_polish_model(active_polish_model_ref)
        except RuntimeError as exc:
            detail = str(exc)
            status_code = 503 if "Ollama 服务不可用" in detail else 409
            raise HTTPException(status_code=status_code, detail=detail) from exc

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
        planned_label = f"{active_transcription_model_id}（本地大模型音频转录，实验性）"
    elif active_transcription_engine == TranscriptionEngine.mlx_whisper:
        planned_label = f"{active_transcription_model_id or settings.mlx_whisper_default_model_label}（MLX Whisper）"
    elif active_transcription_engine == TranscriptionEngine.qwen_audio:
        planned_label = f"{settings.qwen_audio_default_model_label}（MLX Audio）"
    elif enable_polish and active_polish_model_id:
        planned_label = f"{planned_model_label(model_id)} + {active_polish_model_id} polish"
    else:
        planned_label = planned_model_label(model_id)
    try:
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
            active_profile.id if enable_polish else None,
            active_profile.label if enable_polish else None,
            (polish_custom_instruction or "").strip() if enable_polish else None,
            active_export_scope,
            base_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    add_event(job_id, "任务已创建")
    add_event(job_id, "模型检查开始")
    checked_models = [model_id]
    if active_transcription_engine in {TranscriptionEngine.ollama_audio, TranscriptionEngine.mlx_whisper, TranscriptionEngine.qwen_audio}:
        checked_models = [active_transcription_model_id]
    if enable_polish and active_polish_model_id:
        checked_models.append(active_polish_model_id)
    add_event(job_id, f"模型检查完成：{', '.join(model for model in checked_models if model)}")
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
        active_profile.id,
        (polish_custom_instruction or "").strip() if enable_polish else None,
        active_export_scope,
    )
    return build_status(job)


@app.get("/api/jobs", response_model=list[JobStatus])
def list_jobs() -> list[JobStatus]:
    return [build_status(job) for job in job_store.list()]


@app.delete("/api/jobs/history", response_model=list[JobStatus])
def clear_job_history() -> list[JobStatus]:
    return [build_status(job) for job in job_store.clear_history()]


@app.get("/api/jobs/cleanup/status", response_model=JobWorkFileCleanupStatus)
def get_job_work_file_cleanup_status() -> JobWorkFileCleanupStatus:
    return cleanup_status()


@app.post("/api/jobs/cleanup", response_model=JobWorkFileCleanupStatus)
def clean_job_work_files() -> JobWorkFileCleanupStatus:
    if job_store.has_active_job():
        raise HTTPException(status_code=409, detail="当前有任务正在处理。请等待完成或取消后再清理工作文件。")
    return cleanup_work_files()


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
    if terminal_state(job.state):
        return build_status(job)
    return build_status(job_store.request_cancel(job_id))


@app.post("/api/jobs/{job_id}/polish", response_model=JobStatus)
def rerun_polish(job_id: str, request: PolishRequest) -> JobStatus:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    if not terminal_state(job.state):
        raise HTTPException(status_code=409, detail="当前任务仍在处理，不能重新执行文本整理。")
    if not job.raw_segments:
        raise HTTPException(status_code=409, detail="当前任务没有原始转录结果，不能单独执行文本整理。")

    model_ref = resolve_polish_model(request.model_id or job.polish_model_id)
    if model_ref is None:
        raise HTTPException(status_code=400, detail="请选择文本整理模型")
    model_id = model_ref.path_or_id
    try:
        validate_polish_model(model_ref)
    except RuntimeError as exc:
        detail = str(exc)
        status_code = 503 if "Ollama 服务不可用" in detail else 409
        raise HTTPException(status_code=status_code, detail=detail) from exc

    profile = get_profile(request.profile_id or job.polish_profile_id)
    custom_instruction = (request.custom_instruction or "").strip()
    profile_instruction = combine_instruction(profile, custom_instruction)
    job_store.update(
        job_id,
        state=JobState.polishing,
        progress=74,
        message=f"正在重新执行 {profile.label}",
        error=None,
        enable_polish=True,
        polish_model_id=model_id,
        polish_profile_id=profile.id,
        polish_profile_label=profile.label,
        polish_custom_instruction=custom_instruction or None,
        export_scope=request.export_scope or job.export_scope,
        formats=request.formats or job.formats,
        processing_started_at=utc_now_iso(),
        processing_finished_at=None,
    )
    add_event(job_id, f"重新执行文本整理：{profile.id}")
    try:
        result = polish_segments(
            job.raw_segments,
            model_ref,
            profile_instruction,
            on_event=lambda message, level="info": add_event(job_id, message, level),
            on_warning=lambda warning: append_job_warning(job_id, warning),
        )
        polished = result.segments if result.success_batches else None
        job_store.update(
            job_id,
            polished_segments=polished or [],
            polished_text=segment_text(polished, include_timestamps=False) if polished else None,
            progress=82,
            message="文本整理已完成，正在重新生成导出文件",
        )
        outputs = regenerate_exports(job_id)
        updated = job_store.update(
            job_id,
            state=JobState.completed,
            progress=100,
            message="文本整理已重新生成",
            outputs=outputs,
            processing_finished_at=utc_now_iso(),
        )
        return build_status(updated)
    except Exception as exc:
        warning = f"文本整理重新执行失败，原始转录结果已保留：{exc}"
        append_job_warning(job_id, warning)
        add_event(job_id, warning, "warning")
        updated = job_store.update(
            job_id,
            state=JobState.completed,
            progress=100,
            message=warning,
            error=None,
            error_diagnostic=diagnose_error(str(exc)),
            processing_finished_at=utc_now_iso(),
        )
        return build_status(updated)


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
