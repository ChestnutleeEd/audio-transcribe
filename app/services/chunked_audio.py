from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from app.services.audio_engine import AudioEngineResult
from app.services.exporters import TranscriptSegment, segment_text
from app.services.media import OperationCanceled
from app.services.qwen_audio.audio_preprocess import prepare_audio_chunks
from app.services.qwen_audio.result_formatter import merge_chunks, partial_results


@dataclass(frozen=True)
class ChunkTranscriptionConfig:
    namespace: str
    engine_name: str
    model_label: str
    chunk_seconds: float
    overlap_seconds: float
    metadata: dict[str, object]


@dataclass(frozen=True)
class ChunkTranscriptionItem:
    id: int
    start: float
    end: float
    text: str

    @property
    def chunk_id(self) -> int:
        return self.id

    def to_segment(self) -> TranscriptSegment:
        return TranscriptSegment(start=self.start, end=self.end, text=self.text)


def transcribe_audio_in_chunks(
    *,
    audio_path: Path,
    work_dir: Path,
    config: ChunkTranscriptionConfig,
    transcribe_chunk: Callable[[Path], str],
    is_canceled: Callable[[], bool] = lambda: False,
    on_partial: Callable[[AudioEngineResult], None] | None = None,
) -> tuple[list[TranscriptSegment], list[dict[str, object]]]:
    chunks = prepare_audio_chunks(
        audio_path,
        work_dir,
        chunk_seconds=config.chunk_seconds,
        overlap_seconds=config.overlap_seconds,
        namespace=config.namespace,
        is_canceled=is_canceled,
    )
    completed: list[ChunkTranscriptionItem] = []
    for chunk in chunks:
        if is_canceled():
            raise OperationCanceled("任务已停止")
        text = transcribe_chunk(Path(str(chunk["audio_path"])))
        completed.append(
            ChunkTranscriptionItem(
                id=int(chunk["chunk_id"]),
                start=float(chunk["start"]),
                end=float(chunk["end"]),
                text=text,
            )
        )
        if on_partial:
            partial_segments = merge_chunks(completed)
            partial = partial_results(completed)
            on_partial(
                AudioEngineResult(
                    raw_text=segment_text(partial_segments, include_timestamps=False),
                    segments=partial_segments,
                    metadata={**config.metadata, "partial_results": partial},
                    engine_name=config.engine_name,
                    model_label=config.model_label,
                )
            )

    return merge_chunks(completed), partial_results(completed)
