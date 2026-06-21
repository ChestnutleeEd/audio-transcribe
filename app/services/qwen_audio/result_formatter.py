from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from app.services.exporters import TranscriptSegment, segment_text
from app.services.qwen_audio.audio_preprocess import audio_duration_seconds
from app.services.qwen_audio.qwen_infer import QWEN_AUDIO_BACKEND, QWEN_AUDIO_MODEL_LABEL


@dataclass(frozen=True)
class QwenChunkResult:
    id: int
    start: float
    end: float
    text: str

    def to_segment(self) -> TranscriptSegment:
        return TranscriptSegment(start=self.start, end=self.end, text=self.text)


def merge_chunks(chunks: list[QwenChunkResult]) -> list[TranscriptSegment]:
    merged: list[TranscriptSegment] = []
    for chunk in chunks:
        text = chunk.text.strip()
        if not text:
            continue
        merged.append(chunk.to_segment())
    return merged


def partial_results(chunks: list[QwenChunkResult]) -> list[dict[str, object]]:
    return [asdict(chunk) for chunk in chunks if chunk.text.strip()]


def build_final_json(
    *,
    audio_file: str | Path,
    chunks: list[QwenChunkResult],
    duration: float | None = None,
    model: str = QWEN_AUDIO_MODEL_LABEL,
    backend: str = QWEN_AUDIO_BACKEND,
) -> dict[str, object]:
    audio_path = Path(audio_file)
    if duration is None:
        try:
            duration = audio_duration_seconds(audio_path)
        except Exception:
            duration = max((chunk.end for chunk in chunks), default=0.0)
    segments = partial_results(chunks)
    return {
        "audio_file": str(audio_path),
        "duration": round(float(duration or 0), 3),
        "model": model,
        "backend": backend,
        "segments": segments,
        "full_text": segment_text([QwenChunkResult(**segment).to_segment() for segment in segments], include_timestamps=False),
    }
