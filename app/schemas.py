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


class TranscriptionEngine(str, Enum):
    whisper = "whisper"
    ollama_audio = "ollama_audio"


class OutputFile(BaseModel):
    name: str
    format: OutputFormat
    bytes: int
    download_url: str


class JobEvent(BaseModel):
    time: str
    level: str = "info"
    message: str


class JobStatus(BaseModel):
    id: str
    state: JobState
    progress: int
    message: str
    source_label: str = "未命名任务"
    source_url: str | None = None
    language: str = "auto"
    start_time: str | None = None
    end_time: str | None = None
    processing_started_at: str | None = None
    processing_finished_at: str | None = None
    transcription_engine: TranscriptionEngine = TranscriptionEngine.whisper
    whisper_model_id: str | None = None
    transcription_model_id: str | None = None
    enable_polish: bool = False
    polish_model_id: str | None = None
    model_label: str = "large-v3"
    formats: list[OutputFormat] = Field(default_factory=list)
    include_timestamps: bool = True
    created_at: str | None = None
    outputs: list[OutputFile] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    events: list[JobEvent] = Field(default_factory=list)
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
    canceled = "canceled"


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
    download_progress: int = 0
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    download_progress_label: str | None = None
    message: str
    error: str | None = None


class OllamaModelOption(BaseModel):
    id: str
    label: str
    role: str
    experimental: bool = False
    default: bool = False
    available: bool = False


class OllamaServiceStatus(BaseModel):
    available: bool
    base_url: str
    mock_mode: bool = False
    version: str | None = None
    message: str
    error: str | None = None
    local_models: list[str] = Field(default_factory=list)
    transcription_models: list[OllamaModelOption] = Field(default_factory=list)
    polish_models: list[OllamaModelOption] = Field(default_factory=list)


class OllamaModelCheck(BaseModel):
    model_id: str
    available: bool
    service_available: bool
    message: str
    error: str | None = None


class OllamaPullRequest(BaseModel):
    model_id: str


class OllamaPullStatus(BaseModel):
    model_id: str
    state: ModelDownloadState
    progress: int = 0
    completed_bytes: int | None = None
    total_bytes: int | None = None
    progress_label: str | None = None
    message: str
    error: str | None = None


class OllamaPreflightStatus(BaseModel):
    model_id: str
    task: str
    service_available: bool
    model_exists: bool
    can_generate: bool
    warnings: list[str] = Field(default_factory=list)
    message: str
    error: str | None = None
