from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.schemas import ErrorDiagnostic, ExportScope, JobEvent, JobState, OutputFile, OutputFormat, TranscriptionEngine
from app.services.exporters import TranscriptSegment


@dataclass
class Job:
    id: str
    state: JobState = JobState.queued
    progress: int = 0
    message: str = "等待处理"
    source_label: str = "未命名任务"
    source_url: str | None = None
    language: str = "auto"
    start_time: str | None = None
    end_time: str | None = None
    processing_started_at: str | None = None
    processing_finished_at: str | None = None
    model_id: str = "large-v3"
    transcription_engine: TranscriptionEngine = TranscriptionEngine.qwen_audio
    whisper_model_id: str | None = None
    transcription_model_id: str | None = None
    enable_polish: bool = False
    polish_model_id: str | None = None
    polish_profile_id: str | None = None
    polish_profile_label: str | None = None
    polish_custom_instruction: str | None = None
    model_label: str = "large-v3"
    formats: list[OutputFormat] = field(default_factory=list)
    export_scope: ExportScope = ExportScope.raw
    include_timestamps: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cancel_requested: bool = False
    outputs: list[OutputFile] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    events: list[JobEvent] = field(default_factory=list)
    error: str | None = None
    error_diagnostic: ErrorDiagnostic | None = None
    work_dir: Path | None = None
    base_name: str = "transcript"
    raw_segments: list[TranscriptSegment] = field(default_factory=list)
    polished_segments: list[TranscriptSegment] = field(default_factory=list)
    raw_text: str | None = None
    polished_text: str | None = None
    duration_seconds: float | None = None
    engine_metadata: dict[str, object] = field(default_factory=dict)
    source_path: Path | None = None
    source_dir: Path | None = None
    auto_save_outputs: bool = False
    auto_save_dir: Path | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(
        self,
        job_id: str,
        work_dir: Path,
        source_label: str,
        source_url: str | None,
        language: str,
        start_time: str | None,
        end_time: str | None,
        model_id: str,
        model_label: str,
        formats: list[OutputFormat],
        include_timestamps: bool,
        transcription_engine: TranscriptionEngine = TranscriptionEngine.qwen_audio,
        whisper_model_id: str | None = None,
        transcription_model_id: str | None = None,
        enable_polish: bool = False,
        polish_model_id: str | None = None,
        polish_profile_id: str | None = None,
        polish_profile_label: str | None = None,
        polish_custom_instruction: str | None = None,
        export_scope: ExportScope = ExportScope.raw,
        base_name: str = "transcript",
        source_path: Path | None = None,
        source_dir: Path | None = None,
        auto_save_outputs: bool = False,
        auto_save_dir: Path | None = None,
    ) -> Job:
        job = Job(
            id=job_id,
            work_dir=work_dir,
            source_label=source_label,
            source_url=source_url,
            language=language,
            start_time=start_time,
            end_time=end_time,
            model_id=model_id,
            transcription_engine=transcription_engine,
            whisper_model_id=whisper_model_id,
            transcription_model_id=transcription_model_id,
            enable_polish=enable_polish,
            polish_model_id=polish_model_id,
            polish_profile_id=polish_profile_id,
            polish_profile_label=polish_profile_label,
            polish_custom_instruction=polish_custom_instruction,
            model_label=model_label,
            formats=formats,
            export_scope=export_scope,
            include_timestamps=include_timestamps,
            base_name=base_name,
            source_path=source_path,
            source_dir=source_dir,
            auto_save_outputs=auto_save_outputs,
            auto_save_dir=auto_save_dir,
        )
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)

    def update(self, job_id: str, **changes: object) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            for key, value in changes.items():
                setattr(job, key, value)
            return job

    def add_event(self, job_id: str, message: str, level: str = "info") -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.events.append(JobEvent(time=datetime.now(timezone.utc).isoformat(), level=level, message=message))
            return job

    def list(self) -> list[Job]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def clear_history(self) -> list[Job]:
        terminal = {JobState.completed, JobState.failed, JobState.cancelled}
        with self._lock:
            self._jobs = {job_id: job for job_id, job in self._jobs.items() if job.state not in terminal}
            return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def delete(self, job_id: str) -> Job:
        terminal = {JobState.completed, JobState.failed, JobState.cancelled}
        with self._lock:
            job = self._jobs[job_id]
            if job.state not in terminal:
                raise ValueError("任务仍在处理或排队，请先停止后再删除记录。")
            return self._jobs.pop(job_id)

    def has_active_job(self) -> bool:
        terminal = {JobState.completed, JobState.failed, JobState.cancelled}
        with self._lock:
            return any(job.state not in terminal for job in self._jobs.values())

    def request_cancel(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.cancel_requested = True
            if job.state in {JobState.queued, JobState.validating}:
                job.message = "已取消排队任务"
            else:
                job.message = "正在停止任务"
            job.state = JobState.cancelled
            job.progress = 100
            return job


job_store = JobStore()
