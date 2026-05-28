from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.schemas import AppOptions, JobState, JobStatus, ModelSelection, OptionItem, OutputFile, OutputFormat
from app.services.exporters import export_transcript
from app.services.jobs import Job, job_store
from app.services.media import (
    OperationCanceled,
    SUPPORTED_UPLOAD_SUFFIXES,
    download_audio,
    ensure_runtime_dirs,
    normalize_audio,
    safe_stem,
)
from app.services.model_manager import current_model_id, download_model, model_status, select_model, set_runtime_device
from app.services.transcriber import transcribe_audio


app = FastAPI(title=settings.app_name)
executor = ThreadPoolExecutor(max_workers=1)


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
        language=job.language,
        start_time=job.start_time,
        end_time=job.end_time,
        model_label=job.model_label,
        formats=job.formats,
        include_timestamps=job.include_timestamps,
        created_at=job.created_at,
        outputs=job.outputs,
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
) -> None:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        return

    try:
        if job.cancel_requested:
            job_store.update(job_id, state=JobState.canceled, progress=100, message="已取消排队任务")
            return

        job_store.update(job_id, state=JobState.running, progress=8, message="准备音频来源")
        work_dir = job.work_dir
        media_path = source_path
        if media_path is None and source_url:
            media_path = download_audio(source_url, work_dir, lambda: is_job_canceled(job_id))
            base_name = safe_stem(media_path.name)

        if media_path is None:
            raise ValueError("缺少上传文件或视频链接")

        if is_job_canceled(job_id):
            raise OperationCanceled("任务已停止")

        job_store.update(job_id, progress=24, message="转换为 Whisper 友好的音频")
        wav_path = work_dir / "input_16k.wav"
        normalize_audio(media_path, wav_path, start_time, end_time, lambda: is_job_canceled(job_id))

        job_store.update(job_id, progress=42, message=f"加载 {model_id} 模型")

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

        segments = transcribe_audio(
            wav_path,
            language,
            lambda: is_job_canceled(job_id),
            update_transcribe_status,
            model_id,
        )
        if not segments:
            raise RuntimeError("没有识别到可用文本")

        if is_job_canceled(job_id):
            raise OperationCanceled("任务已停止")

        job_store.update(job_id, progress=82, message="生成转录文件")
        output_paths = export_transcript(work_dir, base_name, formats, segments, include_timestamps)
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
        )
    except OperationCanceled as exc:
        job_store.update(job_id, state=JobState.canceled, progress=100, message=str(exc), error=None)
    except Exception as exc:
        job_store.update(job_id, state=JobState.failed, progress=100, message="任务失败", error=str(exc))


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
            OptionItem(value="docx", label="Word"),
            OptionItem(value="txt", label="TXT"),
            OptionItem(value="md", label="Markdown"),
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


@app.post("/api/jobs", response_model=JobStatus)
async def create_job(
    file: UploadFile | None = File(default=None),
    source_url: str | None = Form(default=None),
    language: str = Form(default="auto"),
    formats: str = Form(default="docx,txt"),
    include_timestamps: bool = Form(default=True),
    start_time: str | None = Form(default=None),
    end_time: str | None = Form(default=None),
) -> JobStatus:
    has_file = bool(file and file.filename)
    clean_source_url = source_url.strip() if source_url else None

    if not has_file and not clean_source_url:
        raise HTTPException(status_code=400, detail="请上传本地文件或填写视频链接")

    try:
        parsed_formats = parse_formats(formats)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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

    model_id = current_model_id()
    job = job_store.create(
        job_id,
        work_dir,
        source_label,
        language,
        start_time,
        end_time,
        model_id,
        planned_model_label(model_id),
        parsed_formats,
        include_timestamps,
    )
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
