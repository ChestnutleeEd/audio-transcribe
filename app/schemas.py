from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    docx = "docx"


class JobState(str, Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


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
    source_label: str = "未命名任务"
    language: str = "auto"
    start_time: str | None = None
    end_time: str | None = None
    model_label: str = "large-v3"
    formats: list[OutputFormat] = Field(default_factory=list)
    include_timestamps: bool = True
    created_at: str | None = None
    outputs: list[OutputFile] = Field(default_factory=list)
    error: str | None = None


class OptionItem(BaseModel):
    value: str
    label: str


class AppOptions(BaseModel):
    languages: list[OptionItem]
    formats: list[OptionItem]
    timestamp_modes: list[OptionItem]
    supported_sources: list[Literal["upload", "url"]]


class ModelDownloadState(str, Enum):
    idle = "idle"
    downloading = "downloading"
    completed = "completed"
    failed = "failed"


class ModelOption(BaseModel):
    id: str
    label: str
    repo_id: str
    managed_path: str
    available: bool


class ModelSelection(BaseModel):
    model_id: str


class ModelStatus(BaseModel):
    available: bool
    selected_model: str
    models: list[ModelOption]
    active_path: str | None = None
    managed_path: str
    repo_id: str
    required_files: list[str]
    configured_device: str
    active_device: str | None = None
    active_compute_type: str | None = None
    download_state: ModelDownloadState
    message: str
    error: str | None = None
