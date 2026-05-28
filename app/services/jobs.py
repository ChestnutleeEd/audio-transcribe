from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.schemas import JobState, OutputFile


@dataclass
class Job:
    id: str
    state: JobState = JobState.queued
    progress: int = 0
    message: str = "等待处理"
    source_label: str = "未命名任务"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    cancel_requested: bool = False
    outputs: list[OutputFile] = field(default_factory=list)
    error: str | None = None
    work_dir: Path | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(self, job_id: str, work_dir: Path, source_label: str) -> Job:
        job = Job(id=job_id, work_dir=work_dir, source_label=source_label)
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
                job.state = JobState.canceled
                job.progress = 100
                job.message = "已取消排队任务"
            return job


job_store = JobStore()
