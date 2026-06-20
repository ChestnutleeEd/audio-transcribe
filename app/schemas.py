from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    txt = "txt"
    md = "md"
    json = "json"
    srt = "srt"
    docx = "docx"


class ExportScope(str, Enum):
    raw = "raw"
    polished = "polished"
    both = "both"


class JobState(str, Enum):
    validating = "validating"
    preparing_model = "preparing_model"
    transcribing = "transcribing"
    polishing = "polishing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class TranscriptionEngine(str, Enum):
    whisper = "whisper"
    mlx_whisper = "mlx-whisper"
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


class ErrorDiagnostic(BaseModel):
    code: str
    title: str
    message: str
    action: str
    technical_detail: str | None = None


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
    polish_profile_id: str | None = None
    polish_profile_label: str | None = None
    polish_custom_instruction: str | None = None
    model_label: str = "large-v3"
    formats: list[OutputFormat] = Field(default_factory=list)
    export_scope: ExportScope = ExportScope.raw
    include_timestamps: bool = True
    created_at: str | None = None
    outputs: list[OutputFile] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    events: list[JobEvent] = Field(default_factory=list)
    error: str | None = None
    error_diagnostic: ErrorDiagnostic | None = None
    raw_text: str | None = None
    polished_text: str | None = None
    has_segments: bool = False
    duration_seconds: float | None = None


class OptionItem(BaseModel):
    value: str
    label: str


class AppOptions(BaseModel):
    languages: list[OptionItem]
    formats: list[OptionItem]
    timestamp_modes: list[OptionItem]
    supported_sources: list[Literal["upload", "url"]]


class PolishProfile(BaseModel):
    id: str
    label: str
    description: str
    prompt_preview: str | None = None


class PolishRequest(BaseModel):
    model_id: str | None = None
    profile_id: str | None = None
    custom_instruction: str | None = None
    export_scope: ExportScope | None = None
    formats: list[OutputFormat] | None = None


class HealthCheckItem(BaseModel):
    id: str
    label: str
    status: Literal["success", "warning", "error"]
    message: str
    suggestion: str | None = None


class HealthCheckStatus(BaseModel):
    checked_at: str
    items: list[HealthCheckItem]


class MLXWhisperStatus(BaseModel):
    engine: str = "mlx-whisper"
    available: bool
    platform_supported: bool
    dependency_installed: bool
    model_configured: bool
    ffmpeg_available: bool
    is_macos: bool
    is_apple_silicon: bool
    os: str
    arch: str
    model_path_or_repo: str = ""
    default_model_label: str = "whisper-large-v3-mlx"
    language: str = "auto"
    reason: str | None = None
    hint: str | None = None


class ModelDownloadState(str, Enum):
    idle = "idle"
    downloading = "downloading"
    completed = "completed"
    failed = "failed"
    canceled = "canceled"


class WhisperModelMeta(BaseModel):
    speed: str
    accuracy: str
    resource: str
    recommended_for: list[str] = Field(default_factory=list)
    mac_m4_air_advice: str
    default_recommended: bool = False
    positioning: str
    description: str


class ModelOption(BaseModel):
    id: str
    label: str
    repo_id: str
    managed_path: str
    available: bool
    meta: WhisperModelMeta | None = None


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


class LocalDetectedModel(BaseModel):
    provider_id: str
    provider: str
    provider_type: str
    name: str
    id: str
    size: int | None = None
    size_label: str | None = None
    modified_at: str | None = None
    can_polish: bool = False
    recommendation: str | None = None


class LocalModelProviderStatus(BaseModel):
    id: str
    name: str
    type: str
    url: str
    online: bool = False
    can_polish: bool = False
    message: str
    error: str | None = None
    models: list[LocalDetectedModel] = Field(default_factory=list)


class LocalModelDetectionStatus(BaseModel):
    checked_at: str
    providers_checked: int
    providers_online: int
    models_found: int
    message: str
    providers: list[LocalModelProviderStatus] = Field(default_factory=list)
