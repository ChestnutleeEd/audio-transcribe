from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.schemas import JobState, OutputFile, OutputFormat


@dataclass
class Job:
    id: str
    state: JobState = JobState.queued
    progress: int = 0
    message: str = "等待处理"
    source_label: str = "未命名任务"
    language: str = "auto"
    start_time: str | None = None
    end_time: str | None = None
    model_id: str = "large-v3"
    model_label: str = "large-v3"
    formats: list[OutputFormat] = field(default_factory=list)
    include_timestamps: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cancel_requested: bool = False
    outputs: list[OutputFile] = field(default_factory=list)
    error: str | None = None
    work_dir: Path | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(
        self,
        job_id: str,
        work_dir: Path,
        source_label: str,
        language: str,
        start_time: str | None,
        end_time: str | None,
        model_id: str,
        model_label: str,
        formats: list[OutputFormat],
        include_timestamps: bool,
    ) -> Job:
        job = Job(
            id=job_id,
            work_dir=work_dir,
            source_label=source_label,
            language=language,
            start_time=start_time,
            end_time=end_time,
            model_id=model_id,
            model_label=model_label,
            formats=formats,
            include_timestamps=include_timestamps,
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

    def list(self) -> list[Job]:
        with self._lock:
            return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def request_cancel(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs[job_id]
            job.cancel_requested = True
            if job.state == JobState.queued:
                job.message = "已取消排队任务"
            else:
                job.message = "正在停止任务"
            job.state = JobState.canceled
            job.progress = 100
            return job


job_store = JobStore()
