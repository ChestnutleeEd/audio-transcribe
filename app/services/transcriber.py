from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from faster_whisper import WhisperModel

from app.config import settings
from app.services.exporters import TranscriptSegment


def configure_runtime() -> None:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    dll_dirs = os.getenv("AUDIO_TRANSCRIBE_DLL_DIRS", "")
    for raw_dir in [item.strip() for item in dll_dirs.split(os.pathsep) if item.strip()]:
        path = Path(raw_dir)
        if path.exists() and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(path))


@lru_cache(maxsize=1)
def get_model() -> WhisperModel:
    configure_runtime()
    if not settings.model_path.exists():
        raise FileNotFoundError(f"未找到 Whisper 模型目录: {settings.model_path}")
    return WhisperModel(str(settings.model_path), device=settings.device, compute_type=settings.compute_type)


def transcribe_audio(audio_path: Path, language: str | None) -> list[TranscriptSegment]:
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
    return [
        TranscriptSegment(start=segment.start, end=segment.end, text=segment.text.strip())
        for segment in segments
        if segment.text.strip()
    ]
