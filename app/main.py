from __future__ import annotations

import shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import ROOT_DIR, settings
from app.schemas import AppOptions, JobState, JobStatus, OptionItem, OutputFile, OutputFormat
from app.services.exporters import export_transcript
from app.services.jobs import Job, job_store
from app.services.media import SUPPORTED_UPLOAD_SUFFIXES, download_audio, ensure_runtime_dirs, normalize_audio, safe_stem
from app.services.model_manager import download_model, model_status
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
        outputs=job.outputs,
        error=job.error,
    )


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
) -> None:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        return

    try:
        job_store.update(job_id, state=JobState.running, progress=8, message="准备音频来源")
        work_dir = job.work_dir
        media_path = source_path
        if source_url:
            media_path = download_audio(source_url, work_dir)
            base_name = safe_stem(media_path.name)

        if media_path is None:
            raise ValueError("缺少上传文件或视频链接")

        job_store.update(job_id, progress=24, message="转换为 Whisper 友好的音频")
        wav_path = work_dir / "input_16k.wav"
        normalize_audio(media_path, wav_path, start_time, end_time)

        job_store.update(job_id, progress=42, message="加载模型并转写")
        segments = transcribe_audio(wav_path, language)
        if not segments:
            raise RuntimeError("没有识别到可用文本")

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
            message="转录完成，下载后会自动删除对应文件",
            outputs=outputs,
        )
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


@app.post("/api/model/download")
def start_model_download():
    status = model_status()
    if status.available:
        return status
    if status.download_state == "downloading":
        return status
    executor.submit(download_model)
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
    if not file and not source_url:
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

    if file:
        suffix = Path(file.filename or "").suffix.lower()
        if suffix not in SUPPORTED_UPLOAD_SUFFIXES:
            raise HTTPException(status_code=400, detail=f"暂不支持该文件格式: {suffix or '未知'}")
        base_name = safe_stem(file.filename or "upload")
        source_path = work_dir / f"source{suffix}"
        with source_path.open("wb") as handle:
            shutil.copyfileobj(file.file, handle)
    elif source_url:
        base_name = safe_stem(source_url)

    job = job_store.create(job_id, work_dir)
    executor.submit(
        run_job,
        job_id,
        source_path,
        source_url,
        base_name,
        language,
        parsed_formats,
        include_timestamps,
        start_time,
        end_time,
    )
    return build_status(job)


@app.get("/api/jobs/{job_id}", response_model=JobStatus)
def get_job(job_id: str) -> JobStatus:
    job = job_store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return build_status(job)


@app.get("/api/jobs/{job_id}/download/{filename}")
def download_output(job_id: str, filename: str, background_tasks: BackgroundTasks) -> FileResponse:
    job = job_store.get(job_id)
    if job is None or job.work_dir is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    path = job.work_dir / Path(filename).name
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在或已被删除")
    background_tasks.add_task(unlink_file, path)
    return FileResponse(path, filename=path.name)


static_dir = ROOT_DIR / "static"
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
