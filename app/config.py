from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ModelDefinition:
    id: str
    label: str
    repo_id: str
    local_dir: str


@dataclass(frozen=True)
class OllamaModelDefinition:
    id: str
    label: str
    role: str
    experimental: bool = False
    default: bool = False


SUPPORTED_MODELS: tuple[ModelDefinition, ...] = (
    ModelDefinition("tiny", "faster-whisper tiny", "Systran/faster-whisper-tiny", "tiny-local"),
    ModelDefinition("base", "faster-whisper base", "Systran/faster-whisper-base", "base-local"),
    ModelDefinition("small", "faster-whisper small", "Systran/faster-whisper-small", "small-local"),
    ModelDefinition("medium", "faster-whisper medium", "Systran/faster-whisper-medium", "medium-local"),
    ModelDefinition("large-v3", "faster-whisper large-v3", "Systran/faster-whisper-large-v3", "large-v3-local"),
)

OLLAMA_TRANSCRIPTION_MODELS: tuple[OllamaModelDefinition, ...] = (
    OllamaModelDefinition(
        "gemma4:12b",
        "Gemma 4 12B",
        "direct audio transcription",
        experimental=True,
        default=True,
    ),
)

OLLAMA_POLISH_MODELS: tuple[OllamaModelDefinition, ...] = (
    OllamaModelDefinition("gemma4:12b", "Gemma 4 12B", "high quality polish", default=True),
    OllamaModelDefinition("gemma3:1b", "Gemma 3 1B", "lightweight polish"),
)


@dataclass(frozen=True)
class Settings:
    app_name: str = "Audio Transcribe"
    managed_model_path: Path = ROOT_DIR / "models" / "large-v3-local"
    legacy_model_path: Path = ROOT_DIR / "origin-code" / "large-v3-local"
    model_repo_id: str = os.getenv("AUDIO_TRANSCRIBE_MODEL_REPO_ID", "Systran/faster-whisper-large-v3")
    default_model_id: str = os.getenv("AUDIO_TRANSCRIBE_MODEL_ID", "large-v3")
    model_path: Path = Path(os.getenv("AUDIO_TRANSCRIBE_MODEL_PATH", managed_model_path))
    device: str = os.getenv("AUDIO_TRANSCRIBE_DEVICE", "cuda")
    compute_type: str = os.getenv("AUDIO_TRANSCRIBE_COMPUTE_TYPE", "int8_float16")
    ffmpeg_path: str = os.getenv("AUDIO_TRANSCRIBE_FFMPEG", str(ROOT_DIR / "origin-code" / "ffmpeg.exe"))
    data_dir: Path = Path(os.getenv("AUDIO_TRANSCRIBE_DATA_DIR", ROOT_DIR / "data"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_ollama_transcription_model_id: str = os.getenv("OLLAMA_TRANSCRIPTION_MODEL_ID", "gemma4:12b")
    default_ollama_polish_model_id: str = os.getenv("OLLAMA_POLISH_MODEL_ID", "gemma4:12b")
    mock_mode: bool = os.getenv("AUDIO_TRANSCRIBE_MOCK", "0") in {"1", "true", "True", "yes", "YES"}
    mock_polish_fail: bool = os.getenv("AUDIO_TRANSCRIBE_MOCK_POLISH_FAIL", "0") in {"1", "true", "True", "yes", "YES"}

    @property
    def jobs_dir(self) -> Path:
        return self.data_dir / "jobs"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"

    def model_definition(self, model_id: str | None = None) -> ModelDefinition:
        selected_id = model_id or self.default_model_id
        for model in SUPPORTED_MODELS:
            if model.id == selected_id:
                if model.id == "large-v3" and self.model_repo_id != model.repo_id:
                    return ModelDefinition(model.id, model.label, self.model_repo_id, model.local_dir)
                return model
        return SUPPORTED_MODELS[-1]

    def managed_model_path_for(self, model_id: str | None = None) -> Path:
        return ROOT_DIR / "models" / self.model_definition(model_id).local_dir

    def candidate_model_paths(self, model_id: str | None = None) -> list[Path]:
        model = self.model_definition(model_id)
        managed_path = self.managed_model_path_for(model.id)
        candidates = [managed_path]
        if model.id == "large-v3":
            candidates = [self.model_path, managed_path, self.legacy_model_path]
        unique: list[Path] = []
        for candidate in candidates:
            if candidate not in unique:
                unique.append(candidate)
        return unique

    def ollama_transcription_model_definition(self, model_id: str | None = None) -> OllamaModelDefinition:
        selected_id = model_id or self.default_ollama_transcription_model_id
        for model in OLLAMA_TRANSCRIPTION_MODELS:
            if model.id == selected_id:
                return model
        return OLLAMA_TRANSCRIPTION_MODELS[0]

    def ollama_polish_model_definition(self, model_id: str | None = None) -> OllamaModelDefinition:
        selected_id = model_id or self.default_ollama_polish_model_id
        for model in OLLAMA_POLISH_MODELS:
            if model.id == selected_id:
                return model
        return OLLAMA_POLISH_MODELS[0]


settings = Settings()
