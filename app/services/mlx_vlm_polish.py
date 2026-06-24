from __future__ import annotations

import math
import subprocess
import time
from collections.abc import Callable

from app.config import settings
from app.services.exporters import TranscriptSegment
from app.services.mlx_vlm_audio_provider import clean_transcript_text, mlx_vlm_audio_status, parse_mlx_vlm_generate_output
from app.services.ollama_provider import PolishResult, build_polish_prompt, parse_polish_response, resolve_polish_batch_size


def publish_event(callback: Callable[[str, str], None] | None, message: str, level: str = "info") -> None:
    if callback:
        callback(message, level)


def publish_warning(callback: Callable[[str], None] | None, warning: str) -> None:
    if callback:
        callback(warning)


def generate_text(model_path_or_repo: str, prompt: str, python_executable: str | None = None) -> str:
    executable = (python_executable or settings.mlx_vlm_python).strip()
    command = [
        executable,
        "-m",
        "mlx_vlm.generate",
        "--model",
        model_path_or_repo,
        "--prompt",
        prompt,
        "--max-tokens",
        str(settings.mlx_vlm_polish_max_tokens),
        "--temperature",
        "0",
        "--no-verbose",
    ]
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
    except OSError as exc:
        raise RuntimeError(f"无法启动 Gemma4 MLX VLM 文本整理：{exc}") from exc

    started_at = time.monotonic()
    try:
        while process.poll() is None:
            if time.monotonic() - started_at > settings.mlx_vlm_timeout_seconds:
                process.kill()
                raise RuntimeError(f"Gemma4 MLX VLM 文本整理超时：超过 {settings.mlx_vlm_timeout_seconds} 秒")
            try:
                stdout, stderr = process.communicate(timeout=0.5)
            except subprocess.TimeoutExpired:
                continue
            break
        else:
            stdout, stderr = process.communicate()
    except subprocess.TimeoutExpired as exc:
        process.kill()
        raise RuntimeError(f"Gemma4 MLX VLM 文本整理超时：{exc}") from exc

    if process.returncode != 0:
        detail = (stderr or stdout or "").strip()
        raise RuntimeError(f"Gemma4 MLX VLM 文本整理失败：{detail}")
    text = clean_transcript_text(parse_mlx_vlm_generate_output(stdout))
    if not text:
        detail = (stderr or stdout or "").strip()
        raise RuntimeError(f"Gemma4 MLX VLM 文本整理未返回文本：{detail}")
    return text


def polish_segments_with_mlx_vlm(
    segments: list[TranscriptSegment],
    model_path_or_repo: str,
    profile_instruction: str | None = None,
    on_event: Callable[[str, str], None] | None = None,
    on_warning: Callable[[str], None] | None = None,
) -> PolishResult:
    if not segments:
        return PolishResult(success=True, segments=segments)

    status = mlx_vlm_audio_status(model_path_or_repo)
    if not status.available:
        raise RuntimeError(status.reason or "Gemma4 MLX VLM 文本整理模型不可用")

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
        publish_event(on_event, f"MLX VLM 文本整理分批开始：{batch_index}/{total_batches}，{event_range}")
        try:
            prompt = build_polish_prompt(batch, profile_instruction)
            response = generate_text(model_path_or_repo, prompt, status.python_executable)
            polished_batch = parse_polish_response(response, batch)
            output_segments[start:end] = polished_batch
            success_batches += 1
            publish_event(on_event, f"MLX VLM 文本整理分批完成：{batch_index}/{total_batches}")
        except Exception as exc:
            failed_batches += 1
            warning = (
                f"MLX VLM 文本整理分批失败：{batch_index}/{total_batches}，{event_range}，原因：{exc}。"
                "该批次已保留原始转录文本。"
            )
            warnings.append(warning)
            publish_warning(on_warning, warning)
            publish_event(on_event, f"MLX VLM 文本整理分批失败：{batch_index}/{total_batches}，原因：{exc}", "warning")
            output_segments[start:end] = batch

    publish_event(
        on_event,
        f"MLX VLM 文本整理完成：成功批次={success_batches}，失败批次={failed_batches}",
        "warning" if failed_batches else "info",
    )
    return PolishResult(
        success=failed_batches == 0,
        segments=output_segments,
        warnings=warnings,
        success_batches=success_batches,
        failed_batches=failed_batches,
    )
