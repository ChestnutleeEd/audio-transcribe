from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Callable

from faster_whisper import WhisperModel

from app.config import ROOT_DIR, settings
from app.services.exporters import TranscriptSegment
from app.services.model_manager import resolve_model_path


def configure_runtime() -> None:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    default_dirs = [ROOT_DIR / "origin-code"]
    env_dirs = [Path(item.strip()) for item in os.getenv("AUDIO_TRANSCRIBE_DLL_DIRS", "").split(os.pathsep) if item.strip()]
    for path in [*default_dirs, *env_dirs]:
        if path.exists() and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(path))


def create_model(model_path: Path, device: str, compute_type: str) -> WhisperModel:
    return WhisperModel(str(model_path), device=device, compute_type=compute_type)


def is_cuda_library_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in ["cublas", "cudnn", "cuda", "could not load library", "cannot be loaded"])


def cpu_fallback_enabled() -> bool:
    return os.getenv("AUDIO_TRANSCRIBE_CPU_FALLBACK", "1") not in {"0", "false", "False"}


@lru_cache(maxsize=1)
def get_model() -> WhisperModel:
    configure_runtime()
    model_path = resolve_model_path()
    if model_path is None:
        raise FileNotFoundError(
            f"未找到 Whisper 模型目录。请下载模型到 {settings.managed_model_path}，"
            f"或设置 AUDIO_TRANSCRIBE_MODEL_PATH。"
        )
    try:
        return create_model(model_path, settings.device, settings.compute_type)
    except Exception as exc:
        if settings.device == "cuda" and cpu_fallback_enabled() and is_cuda_library_error(exc):
            return create_model(model_path, "cpu", "int8")
        raise


def transcribe_audio(
    audio_path: Path,
    language: str | None,
    is_canceled: Callable[[], bool] = lambda: False,
) -> list[TranscriptSegment]:
    model = get_model()
    whisper_language = None if language in {None, "", "auto"} else language
    segments, _info = model.transcribe(
        str(audio_path),
        beam_size=5,
        language=whisper_language,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 500},
        condition_on_previous_text=False,
    )
    transcript: list[TranscriptSegment] = []
    for segment in segments:
        if is_canceled():
            raise RuntimeError("任务已停止")
        text = segment.text.strip()
        if text:
            transcript.append(TranscriptSegment(start=segment.start, end=segment.end, text=text))
    return transcript
