from __future__ import annotations

import math
from collections.abc import Callable

import numpy as np

from app.config import settings
from app.services.exporters import TranscriptSegment
from app.services.ollama_provider import (
    PolishResult,
    build_polish_prompt,
    parse_polish_response,
    resolve_polish_batch_size,
)
from app.services.qwen_audio.qwen_infer import load_qwen_audio_model, qwen_offline_env


def publish_event(callback: Callable[[str, str], None] | None, message: str, level: str = "info") -> None:
    if callback:
        callback(message, level)


def publish_warning(callback: Callable[[str], None] | None, warning: str) -> None:
    if callback:
        callback(warning)


def silent_audio_placeholder() -> np.ndarray:
    return np.zeros(1600, dtype=np.float32)


def generate_text(model_path_or_repo: str, prompt: str) -> str:
    model = load_qwen_audio_model(model_path_or_repo)
    with qwen_offline_env(model_path_or_repo):
        result = model.generate(
            silent_audio_placeholder(),
            prompt=(
                "The audio input is intentionally silent and must be ignored. "
                "Follow only the text instruction below.\n\n"
                f"{prompt}"
            ),
            max_tokens=2048,
            temperature=0.0,
        )
    text = getattr(result, "text", None)
    if text is None:
        text = result.get("text") if isinstance(result, dict) else str(result)
    return str(text or "").strip()


def polish_segments_with_qwen_audio(
    segments: list[TranscriptSegment],
    model_path_or_repo: str,
    profile_instruction: str | None = None,
    on_event: Callable[[str, str], None] | None = None,
    on_warning: Callable[[str], None] | None = None,
) -> PolishResult:
    if not segments:
        return PolishResult(success=True, segments=segments)

    batch_size = resolve_polish_batch_size(model_path_or_repo)
    total_batches = math.ceil(len(segments) / batch_size)
    output_segments = list(segments)
    warnings: list[str] = []
    success_batches = 0
    failed_batches = 0

    for batch_index, start in enumerate(range(0, len(segments), batch_size), start=1):
        end = min(start + batch_size, len(segments))
        batch = segments[start:end]
        event_range = f"segments {start}-{end - 1}"
        publish_event(on_event, f"MLX Audio 文本整理分批开始：{batch_index}/{total_batches}，{event_range}")
        try:
            prompt = build_polish_prompt(batch, profile_instruction)
            response = generate_text(model_path_or_repo, prompt)
            polished_batch = parse_polish_response(response, batch)
            output_segments[start:end] = polished_batch
            success_batches += 1
            publish_event(on_event, f"MLX Audio 文本整理分批完成：{batch_index}/{total_batches}")
        except Exception as exc:
            failed_batches += 1
            warning = (
                f"MLX Audio 文本整理分批失败：{batch_index}/{total_batches}，{event_range}，原因：{exc}。"
                "该批次已保留原始转录文本。"
            )
            warnings.append(warning)
            publish_warning(on_warning, warning)
            publish_event(on_event, f"MLX Audio 文本整理分批失败：{batch_index}/{total_batches}，原因：{exc}", "warning")
            output_segments[start:end] = batch

    publish_event(
        on_event,
        f"MLX Audio 文本整理完成：成功批次={success_batches}，失败批次={failed_batches}",
        "warning" if failed_batches else "info",
    )
    return PolishResult(
        success=failed_batches == 0,
        segments=output_segments,
        warnings=warnings,
        success_batches=success_batches,
        failed_batches=failed_batches,
    )
