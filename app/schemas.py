from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    docx = "docx"


class JobState(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class OutputFile(BaseModel):
    name: str
    format: OutputFormat
    bytes: int
    download_url: str


class JobStatus(BaseModel):
    id: str
    state: JobState
    progress: int
    message: str
    outputs: list[OutputFile] = []
    error: str | None = None


class OptionItem(BaseModel):
    value: str
    label: str


class AppOptions(BaseModel):
    languages: list[OptionItem]
    formats: list[OptionItem]
    timestamp_modes: list[OptionItem]
    supported_sources: list[Literal["upload", "url"]]
