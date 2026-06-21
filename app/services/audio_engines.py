from __future__ import annotations

from pathlib import Path
from typing import Callable

from app.config import settings
from app.services.audio_engine import AudioEngineResult
from app.services.mlx_whisper_provider import transcribe_with_mlx_whisper
from app.services.qwen_audio.stream_engine import QwenAudioEngine
from app.services.transcriber import transcribe_audio


class WhisperAudioEngine:
    name = "whisper"

    def __init__(
        self,
        *,
        model_id: str,
        on_status: Callable[[str, dict[str, str] | None], None] | None = None,
    ) -> None:
        self.model_id = model_id
        self.on_status = on_status

    def transcribe(
        self,
        audio_path: Path,
        language: str | None,
        is_canceled: Callable[[], bool] = lambda: False,
        on_partial: Callable[[AudioEngineResult], None] | None = None,
    ) -> AudioEngineResult:
        del on_partial
        segments = transcribe_audio(audio_path, language, is_canceled, self.on_status, self.model_id)
        return AudioEngineResult.from_segments(
            segments=segments,
            engine_name=self.name,
            model_label=self.model_id,
            metadata={"engine": self.name, "model": self.model_id, "backend": "faster-whisper"},
        )


class MLXWhisperAudioEngine:
    name = "mlx-whisper"

    def __init__(self, *, model_path_or_repo: str | None = None) -> None:
        self.model_path_or_repo = (model_path_or_repo or settings.mlx_whisper_model_path_or_repo).strip()

    def transcribe(
        self,
        audio_path: Path,
        language: str | None,
        is_canceled: Callable[[], bool] = lambda: False,
        on_partial: Callable[[AudioEngineResult], None] | None = None,
    ) -> AudioEngineResult:
        del is_canceled, on_partial
        segments = transcribe_with_mlx_whisper(audio_path, self.model_path_or_repo, language)
        return AudioEngineResult.from_segments(
            segments=segments,
            engine_name=self.name,
            model_label=f"{self.model_path_or_repo or settings.mlx_whisper_default_model_label}（MLX Whisper）",
            metadata={"engine": self.name, "model": self.model_path_or_repo, "backend": "mlx-whisper"},
        )


__all__ = ["MLXWhisperAudioEngine", "QwenAudioEngine", "WhisperAudioEngine"]
