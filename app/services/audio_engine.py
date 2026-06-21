from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Protocol

from app.services.exporters import TranscriptSegment, segment_text


@dataclass(frozen=True)
class AudioEngineResult:
    raw_text: str
    segments: list[TranscriptSegment]
    metadata: dict[str, object]
    engine_name: str
    model_label: str
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def from_segments(
        cls,
        *,
        segments: list[TranscriptSegment],
        engine_name: str,
        model_label: str,
        metadata: dict[str, object] | None = None,
        warnings: list[str] | None = None,
    ) -> "AudioEngineResult":
        return cls(
            raw_text=segment_text(segments, include_timestamps=False),
            segments=segments,
            metadata=metadata or {},
            engine_name=engine_name,
            model_label=model_label,
            warnings=warnings or [],
        )


class AudioEngine(Protocol):
    name: str

    def transcribe(
        self,
        audio_path: Path,
        language: str | None,
        is_canceled: Callable[[], bool] = lambda: False,
        on_partial: Callable[[AudioEngineResult], None] | None = None,
    ) -> AudioEngineResult:
        ...
