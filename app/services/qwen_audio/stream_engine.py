from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterator

from app.config import settings
from app.services.audio_engine import AudioEngineResult
from app.services.exporters import TranscriptSegment, segment_text
from app.services.media import OperationCanceled
from app.services.qwen_audio.audio_preprocess import prepare_audio_chunks
from app.services.qwen_audio.qwen_infer import QWEN_AUDIO_BACKEND, QWEN_AUDIO_MODEL_LABEL, infer_chunk
from app.services.qwen_audio.result_formatter import QwenChunkResult, build_final_json, merge_chunks, partial_results


@dataclass(frozen=True)
class QwenStreamEvent:
    type: str
    chunk: QwenChunkResult | None = None
    segments: list[TranscriptSegment] = field(default_factory=list)
    partial_results: list[dict[str, object]] = field(default_factory=list)
    final_json: dict[str, object] | None = None
    metadata: dict[str, object] = field(default_factory=dict)


def _metadata(
    *,
    audio_file: Path,
    model_path_or_repo: str,
    chunk_seconds: float,
    overlap_seconds: float,
    prompt: str,
    partial: list[dict[str, object]],
    final_json: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "engine": "qwen-audio",
        "backend": QWEN_AUDIO_BACKEND,
        "model": QWEN_AUDIO_MODEL_LABEL,
        "modelPathOrRepo": model_path_or_repo,
        "audioFile": str(audio_file),
        "chunkSeconds": chunk_seconds,
        "overlapSeconds": overlap_seconds,
        "prompt": prompt,
        "partial_results": partial,
        "finalJson": final_json,
    }


def stream_qwen_audio(
    audio_path: Path,
    work_dir: Path,
    model_path_or_repo: str | None = None,
    prompt: str | None = None,
    chunk_seconds: float | None = None,
    overlap_seconds: float | None = None,
    is_canceled: Callable[[], bool] = lambda: False,
) -> Iterator[QwenStreamEvent]:
    active_model = (model_path_or_repo or settings.qwen_audio_model_path_or_repo).strip()
    active_prompt = prompt or settings.qwen_audio_prompt
    active_chunk_seconds = float(chunk_seconds or settings.qwen_audio_chunk_seconds)
    active_overlap_seconds = float(overlap_seconds if overlap_seconds is not None else settings.qwen_audio_overlap_seconds)
    chunks = prepare_audio_chunks(
        audio_path,
        work_dir,
        chunk_seconds=active_chunk_seconds,
        overlap_seconds=active_overlap_seconds,
        is_canceled=is_canceled,
    )
    completed: list[QwenChunkResult] = []
    yield QwenStreamEvent(
        type="prepared",
        metadata=_metadata(
            audio_file=audio_path,
            model_path_or_repo=active_model,
            chunk_seconds=active_chunk_seconds,
            overlap_seconds=active_overlap_seconds,
            prompt=active_prompt,
            partial=[],
        ),
    )

    for chunk in chunks:
        if is_canceled():
            raise OperationCanceled("任务已停止")
        text = infer_chunk(Path(str(chunk["audio_path"])), active_model, active_prompt)
        result = QwenChunkResult(
            id=int(chunk["chunk_id"]),
            start=float(chunk["start"]),
            end=float(chunk["end"]),
            text=text,
        )
        completed.append(result)
        partial = partial_results(completed)
        segments = merge_chunks(completed)
        yield QwenStreamEvent(
            type="chunk",
            chunk=result,
            segments=segments,
            partial_results=partial,
            metadata=_metadata(
                audio_file=audio_path,
                model_path_or_repo=active_model,
                chunk_seconds=active_chunk_seconds,
                overlap_seconds=active_overlap_seconds,
                prompt=active_prompt,
                partial=partial,
            ),
        )

    final_payload = build_final_json(
        audio_file=audio_path,
        chunks=completed,
        model=QWEN_AUDIO_MODEL_LABEL,
        backend=QWEN_AUDIO_BACKEND,
    )
    final_segments = merge_chunks(completed)
    yield QwenStreamEvent(
        type="final",
        segments=final_segments,
        partial_results=partial_results(completed),
        final_json=final_payload,
        metadata=_metadata(
            audio_file=audio_path,
            model_path_or_repo=active_model,
            chunk_seconds=active_chunk_seconds,
            overlap_seconds=active_overlap_seconds,
            prompt=active_prompt,
            partial=partial_results(completed),
            final_json=final_payload,
        ),
    )


class QwenAudioEngine:
    name = "qwen-audio"

    def __init__(
        self,
        *,
        model_path_or_repo: str | None = None,
        prompt: str | None = None,
        chunk_seconds: float | None = None,
        overlap_seconds: float | None = None,
        work_dir: Path | None = None,
    ) -> None:
        self.model_path_or_repo = (model_path_or_repo or settings.qwen_audio_model_path_or_repo).strip()
        self.prompt = prompt or settings.qwen_audio_prompt
        self.chunk_seconds = chunk_seconds
        self.overlap_seconds = overlap_seconds
        self.work_dir = work_dir

    def transcribe(
        self,
        audio_path: Path,
        language: str | None,
        is_canceled: Callable[[], bool] = lambda: False,
        on_partial: Callable[[AudioEngineResult], None] | None = None,
    ) -> AudioEngineResult:
        del language
        if self.work_dir is None:
            raise RuntimeError("QwenAudioEngine 需要 work_dir 才能写入 chunk 文件。")
        final_segments: list[TranscriptSegment] = []
        final_metadata: dict[str, object] = {}
        for event in stream_qwen_audio(
            audio_path,
            self.work_dir,
            model_path_or_repo=self.model_path_or_repo,
            prompt=self.prompt,
            chunk_seconds=self.chunk_seconds,
            overlap_seconds=self.overlap_seconds,
            is_canceled=is_canceled,
        ):
            final_metadata = event.metadata
            if event.type == "chunk":
                final_segments = event.segments
                if on_partial:
                    on_partial(
                        AudioEngineResult(
                            raw_text=segment_text(final_segments, include_timestamps=False),
                            segments=final_segments,
                            metadata=event.metadata,
                            engine_name=self.name,
                            model_label=f"{QWEN_AUDIO_MODEL_LABEL}（MLX Audio）",
                        )
                    )
            elif event.type == "final":
                final_segments = event.segments
                final_metadata = event.metadata
        return AudioEngineResult(
            raw_text=segment_text(final_segments, include_timestamps=False),
            segments=final_segments,
            metadata=final_metadata,
            engine_name=self.name,
            model_label=f"{QWEN_AUDIO_MODEL_LABEL}（MLX Audio）",
        )
