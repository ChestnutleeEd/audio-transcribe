from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from threading import Lock

from app.schemas import JobState, OutputFile


@dataclass
class Job:
    id: str
    state: JobState = JobState.queued
    progress: int = 0
    message: str = "等待处理"
    outputs: list[OutputFile] = field(default_factory=list)
    error: str | None = None
    work_dir: Path | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = Lock()

    def create(self, job_id: str, work_dir: Path) -> Job:
        job = Job(id=job_id, work_dir=work_dir)
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


job_store = JobStore()
