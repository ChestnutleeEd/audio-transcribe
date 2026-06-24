from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_ROOT = Path(os.getenv("AUDIO_TRANSCRIBE_MODEL_ROOT", ROOT_DIR / "models")).expanduser()


@dataclass(frozen=True)
class WhisperModelMeta:
    speed: str
    accuracy: str
    resource: str
    recommended_for: tuple[str, ...]
    mac_m4_air_advice: str
    default_recommended: bool
    positioning: str
    description: str


@dataclass(frozen=True)
class ModelDefinition:
    id: str
    label: str
    repo_id: str
    local_dir: str
    meta: WhisperModelMeta


@dataclass(frozen=True)
class OllamaModelDefinition:
    id: str
    label: str
    role: str
    experimental: bool = False
    default: bool = False


SUPPORTED_MODELS: tuple[ModelDefinition, ...] = (
    ModelDefinition(
        "tiny",
        "faster-whisper tiny",
        "Systran/faster-whisper-tiny",
        "tiny-local",
        WhisperModelMeta(
            speed="极快",
            accuracy="较弱",
            resource="最低",
            recommended_for=("功能测试", "快速预览", "短音频试跑"),
            mac_m4_air_advice="M 系列 MacBook Air 16GB 运行压力最低，但不适合正式中文/日语长音频。",
            default_recommended=False,
            positioning="极轻量测试模型",
            description="tiny 适合确认流程是否跑通，速度极快、资源占用最低，但准确率较弱，不推荐用于正式中文/日语长音频转录。",
        ),
    ),
    ModelDefinition(
        "base",
        "faster-whisper base",
        "Systran/faster-whisper-base",
        "base-local",
        WhisperModelMeta(
            speed="快速",
            accuracy="基础",
            resource="低",
            recommended_for=("快速预览", "低质量要求场景", "较短内容粗转"),
            mac_m4_air_advice="M 系列 MacBook Air 16GB 可以轻松运行，但不建议作为高质量默认模型。",
            default_recommended=False,
            positioning="基础预览模型",
            description="base 比 tiny 更稳，速度仍然很快、资源占用低，适合快速预览和低质量要求场景，不推荐作为高质量默认模型。",
        ),
    ),
    ModelDefinition(
        "small",
        "faster-whisper small",
        "Systran/faster-whisper-small",
        "small-local",
        WhisperModelMeta(
            speed="快",
            accuracy="较高",
            resource="低到中",
            recommended_for=("日常转录", "中文/日语/英语", "长音频", "会议与课程"),
            mac_m4_air_advice="推荐作为 M4 MacBook Air 16GB 默认模型，速度、准确率和资源占用最均衡。",
            default_recommended=True,
            positioning="日常默认模型",
            description="small 是速度、准确率和资源占用最均衡的选择，适合中文、日语、英语的日常转录和大多数长音频任务。",
        ),
    ),
    ModelDefinition(
        "medium",
        "faster-whisper medium",
        "Systran/faster-whisper-medium",
        "medium-local",
        WhisperModelMeta(
            speed="较慢",
            accuracy="高",
            resource="中到高",
            recommended_for=("重要音频", "噪声音频", "课程", "采访", "日语新闻"),
            mac_m4_air_advice="M 系列 MacBook Air 16GB 可以尝试，长音频会更慢并占用更多内存。",
            default_recommended=False,
            positioning="高质量模式",
            description="medium 准确率明显更好，适合重要音频、噪声音频、课程、采访和日语新闻等场景；代价是速度更慢、资源占用更高。",
        ),
    ),
    ModelDefinition(
        "large-v3",
        "faster-whisper large-v3",
        "Systran/faster-whisper-large-v3",
        "large-v3-local",
        WhisperModelMeta(
            speed="慢",
            accuracy="很高",
            resource="高",
            recommended_for=("极限质量模式", "复杂口音", "重要归档", "高价值长音频"),
            mac_m4_air_advice="M4 MacBook Air 16GB 可以尝试，但不建议作为默认长音频模型。",
            default_recommended=False,
            positioning="Whisper 高准确率模型",
            description="large-v3 是 Whisper 系列中准确率很强的模型，适合极限质量模式；资源占用高、速度慢，不建议作为默认长音频模型。",
        ),
    ),
)

OLLAMA_TRANSCRIPTION_MODELS: tuple[OllamaModelDefinition, ...] = (
    OllamaModelDefinition(
        "gemma4:12b-it-qat",
        "Gemma 4 12B IT QAT",
        "音频直转",
        experimental=True,
        default=True,
    ),
)

OLLAMA_POLISH_MODELS: tuple[OllamaModelDefinition, ...] = (
    OllamaModelDefinition("gemma4:12b-it-qat", "Gemma 4 12B IT QAT", "高质量文本整理", default=True),
    OllamaModelDefinition("gemma3:1b", "Gemma 3 1B", "轻量文本整理"),
)


def optional_positive_int_env(name: str) -> int | None:
    value = os.getenv(name)
    if not value:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed > 0 else None


def qwen_audio_default_model_path_or_repo() -> str:
    configured = os.getenv("AUDIO_TRANSCRIBE_QWEN_AUDIO_MODEL")
    if configured:
        return configured
    return ""


def mlx_vlm_default_python() -> str:
    configured = os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_PYTHON")
    if configured:
        return configured
    venv_python = ROOT_DIR / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return str(venv_python)


@dataclass(frozen=True)
class Settings:
    app_name: str = "Audio Transcribe"
    model_root: Path = DEFAULT_MODEL_ROOT
    managed_model_path: Path = DEFAULT_MODEL_ROOT / "large-v3-local"
    legacy_model_path: Path = ROOT_DIR / "origin-code" / "large-v3-local"
    model_repo_id: str = os.getenv("AUDIO_TRANSCRIBE_MODEL_REPO_ID", "Systran/faster-whisper-large-v3")
    default_model_id: str = os.getenv("AUDIO_TRANSCRIBE_MODEL_ID", "large-v3")
    model_path: Path = Path(os.getenv("AUDIO_TRANSCRIBE_MODEL_PATH", managed_model_path))
    device: str = os.getenv("AUDIO_TRANSCRIBE_DEVICE", "cuda")
    compute_type: str = os.getenv("AUDIO_TRANSCRIBE_COMPUTE_TYPE", "int8_float16")
    ffmpeg_path: str = os.getenv("AUDIO_TRANSCRIBE_FFMPEG", str(ROOT_DIR / "origin-code" / "ffmpeg.exe"))
    data_dir: Path = Path(os.getenv("AUDIO_TRANSCRIBE_DATA_DIR", ROOT_DIR / "data"))
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_ollama_transcription_model_id: str = os.getenv("OLLAMA_TRANSCRIPTION_MODEL_ID", "gemma4:12b-it-qat")
    default_ollama_polish_model_id: str = os.getenv("OLLAMA_POLISH_MODEL_ID", "gemma4:12b-it-qat")
    mlx_whisper_enabled: bool = os.getenv("AUDIO_TRANSCRIBE_MLX_WHISPER_ENABLED", "0") in {"1", "true", "True", "yes", "YES"}
    mlx_whisper_model_path_or_repo: str = os.getenv("AUDIO_TRANSCRIBE_MLX_WHISPER_MODEL", "")
    mlx_whisper_default_model_label: str = os.getenv("AUDIO_TRANSCRIBE_MLX_WHISPER_LABEL", "whisper-large-v3-mlx")
    mlx_whisper_language: str = os.getenv("AUDIO_TRANSCRIBE_MLX_WHISPER_LANGUAGE", "auto")
    qwen_audio_model_path_or_repo: str = qwen_audio_default_model_path_or_repo()
    qwen_audio_default_model_label: str = os.getenv("AUDIO_TRANSCRIBE_QWEN_AUDIO_LABEL", "Qwen2-Audio-7B-Instruct-4bit")
    qwen_audio_prompt: str = os.getenv(
        "AUDIO_TRANSCRIBE_QWEN_AUDIO_PROMPT",
        "Transcribe the audio in the original language. Return only the spoken content. Do not add introductions, labels, quotes, translations, or explanations.",
    )
    qwen_audio_chunk_seconds: int = int(os.getenv("AUDIO_TRANSCRIBE_QWEN_AUDIO_CHUNK_SECONDS", "20"))
    qwen_audio_overlap_seconds: int = int(os.getenv("AUDIO_TRANSCRIBE_QWEN_AUDIO_OVERLAP_SECONDS", "1"))
    qwen_audio_allow_download: bool = os.getenv("AUDIO_TRANSCRIBE_QWEN_AUDIO_ALLOW_DOWNLOAD", "0") in {"1", "true", "True", "yes", "YES"}
    mlx_vlm_python: str = mlx_vlm_default_python()
    mlx_vlm_prompt: str = os.getenv(
        "AUDIO_TRANSCRIBE_MLX_VLM_PROMPT",
        "请准确转写这段音频，只输出可听见的人声说话内容本身。"
        "不要添加说明、标签、引号或翻译；如果没有可转写的人声、只有音乐、噪声或静音，请输出空文本，不要解释。"
        "如果是中文，请使用简体中文。",
    )
    mlx_vlm_max_tokens: int = int(os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_MAX_TOKENS", "200"))
    mlx_vlm_polish_max_tokens: int = int(os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_POLISH_MAX_TOKENS", "2048"))
    mlx_vlm_timeout_seconds: int = int(os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_TIMEOUT_SECONDS", "600"))
    mlx_vlm_chunk_seconds: int = int(os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_CHUNK_SECONDS", "20"))
    mlx_vlm_overlap_seconds: int = int(os.getenv("AUDIO_TRANSCRIBE_MLX_VLM_OVERLAP_SECONDS", "1"))
    mock_mode: bool = os.getenv("AUDIO_TRANSCRIBE_MOCK", "0") in {"1", "true", "True", "yes", "YES"}
    mock_polish_fail: bool = os.getenv("AUDIO_TRANSCRIBE_MOCK_POLISH_FAIL", "0") in {"1", "true", "True", "yes", "YES"}
    ollama_polish_batch_size: int | None = optional_positive_int_env("OLLAMA_POLISH_BATCH_SIZE")

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
                    return ModelDefinition(model.id, model.label, self.model_repo_id, model.local_dir, model.meta)
                return model
        return SUPPORTED_MODELS[-1]

    def managed_model_path_for(self, model_id: str | None = None) -> Path:
        return self.model_root / self.model_definition(model_id).local_dir

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
