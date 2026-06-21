from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path

from app.services.exporters import TranscriptSegment, segment_text
from app.services.qwen_audio.qwen_infer import QWEN_AUDIO_BACKEND, QWEN_AUDIO_MODEL_LABEL


@dataclass(frozen=True)
class QwenChunkResult:
    id: int
    start: float
    end: float
    text: str

    def to_segment(self) -> TranscriptSegment:
        return TranscriptSegment(start=self.start, end=self.end, text=self.text)

    @property
    def chunk_id(self) -> int:
        return self.id


def _compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _common_boundary_length(left: str, right: str, max_chars: int = 120) -> int:
    left_text = _compact_text(left)
    right_text = _compact_text(right)
    if not left_text or not right_text:
        return 0
    limit = min(len(left_text), len(right_text), max_chars)
    for size in range(limit, 2, -1):
        if left_text[-size:] == right_text[:size]:
            return size
    return 0


def dedupe_overlap_prefix(previous_text: str, current_text: str, max_chars: int = 120) -> str:
    duplicate_chars = _common_boundary_length(previous_text, current_text, max_chars=max_chars)
    if duplicate_chars <= 0:
        return _compact_text(current_text)
    return _compact_text(current_text)[duplicate_chars:].lstrip(" ，,。.!！?？;；:：、")


def _deduped_chunks(chunks: list[QwenChunkResult]) -> list[QwenChunkResult]:
    deduped: list[QwenChunkResult] = []
    accumulated_text = ""
    previous_end = 0.0
    for chunk in chunks:
        text = dedupe_overlap_prefix(accumulated_text, chunk.text)
        if not text:
            previous_end = max(previous_end, chunk.end)
            continue
        start = max(chunk.start, previous_end)
        deduped.append(QwenChunkResult(id=chunk.id, start=round(start, 3), end=chunk.end, text=text))
        accumulated_text = _compact_text(f"{accumulated_text} {text}")
        previous_end = max(previous_end, chunk.end)
    return deduped


def chunk_to_json_segment(chunk: QwenChunkResult) -> dict[str, object]:
    return {
        "start": round(float(chunk.start), 3),
        "end": round(float(chunk.end), 3),
        "text": chunk.text,
        "chunk_id": chunk.chunk_id,
    }


def merge_chunks(chunks: list[QwenChunkResult]) -> list[TranscriptSegment]:
    merged: list[TranscriptSegment] = []
    for chunk in _deduped_chunks(chunks):
        text = chunk.text.strip()
        if not text:
            continue
        merged.append(chunk.to_segment())
    return merged


def partial_results(chunks: list[QwenChunkResult]) -> list[dict[str, object]]:
    return [chunk_to_json_segment(chunk) for chunk in _deduped_chunks(chunks)]


def build_final_json(
    *,
    audio_file: str | Path,
    chunks: list[QwenChunkResult],
    duration: float | None = None,
    model: str = QWEN_AUDIO_MODEL_LABEL,
    backend: str = QWEN_AUDIO_BACKEND,
) -> dict[str, object]:
    del audio_file, duration, model, backend
    segments = partial_results(chunks)
    return {
        "segments": segments,
        "full_text": segment_text(merge_chunks(chunks), include_timestamps=False),
    }
