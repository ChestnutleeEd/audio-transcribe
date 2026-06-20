from __future__ import annotations

import json
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

from app.config import settings
from app.services.exporters import TranscriptSegment
from app.services.ollama_client import OllamaClient, OllamaError


DIRECT_AUDIO_UNSUPPORTED = "当前 Ollama API 不支持该模型的直接音频输入。"


@dataclass(frozen=True)
class OllamaTranscriptionResult:
    segments: list[TranscriptSegment]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolishResult:
    success: bool
    segments: list[TranscriptSegment]
    warnings: list[str] = field(default_factory=list)
    success_batches: int = 0
    failed_batches: int = 0


def transcribe_audio_direct(audio_path: Path, model_id: str, audio_duration: float | None = None) -> OllamaTranscriptionResult:
    """Direct audio ASR entrypoint for Ollama models.

    The current stable Ollama REST API documents text and image inputs for generation.
    It does not expose a supported audio file field, so this adapter fails explicitly
    instead of embedding audio bytes in a prompt or pretending image input can carry audio.
    """
    if settings.mock_mode:
        end = audio_duration if audio_duration is not None else 8.0
        return OllamaTranscriptionResult(
            segments=[
                TranscriptSegment(
                    start=0.0,
                    end=end,
                    text=f"这是 {model_id} Mock 音频直转的完整转录结果。",
                )
            ],
            warnings=["本地大模型音频转录暂不提供精确分段时间轴。"],
        )
    _ = (audio_path, model_id, audio_duration)
    raise OllamaError(DIRECT_AUDIO_UNSUPPORTED)


def polish_segments(
    segments: list[TranscriptSegment],
    model_id: str,
    profile_instruction: str | None = None,
    client: OllamaClient | None = None,
    on_event: Callable[[str, str], None] | None = None,
    on_warning: Callable[[str], None] | None = None,
) -> PolishResult:
    if not segments:
        return PolishResult(success=True, segments=segments)

    ollama = client or OllamaClient()
    batch_size = resolve_polish_batch_size(model_id)
    total_batches = math.ceil(len(segments) / batch_size)
    output_segments = list(segments)
    warnings: list[str] = []
    success_batches = 0
    failed_batches = 0

    for batch_index, start in enumerate(range(0, len(segments), batch_size), start=1):
        end = min(start + batch_size, len(segments))
        batch = segments[start:end]
        event_range = f"segments {start}-{end - 1}"
        publish_event(on_event, f"文本整理分批开始：{batch_index}/{total_batches}，{event_range}")
        try:
            if settings.mock_mode:
                if settings.mock_polish_fail:
                    raise ValueError("Mock 文本整理失败")
                polished_batch = [
                    TranscriptSegment(start=segment.start, end=segment.end, text=f"{segment.text}（mock polished）")
                    for segment in batch
                ]
            else:
                prompt = build_polish_prompt(batch, profile_instruction)
                result = ollama.generate_text(
                    model_id,
                    prompt,
                    response_format=polish_response_schema(),
                    options={"temperature": 0},
                )
                polished_batch = parse_polish_response(result.response, batch)
            output_segments[start:end] = polished_batch
            success_batches += 1
            publish_event(on_event, f"文本整理分批完成：{batch_index}/{total_batches}")
        except Exception as exc:
            failed_batches += 1
            warning = (
                f"文本整理分批失败：{batch_index}/{total_batches}，{event_range}，原因：{exc}。"
                "该批次已保留原始转录文本。"
            )
            warnings.append(warning)
            publish_warning(on_warning, warning)
            publish_event(on_event, f"文本整理分批失败：{batch_index}/{total_batches}，原因：{exc}", "warning")
            output_segments[start:end] = batch

    publish_event(
        on_event,
        f"文本整理完成：成功批次={success_batches}，失败批次={failed_batches}",
        "warning" if failed_batches else "info",
    )
    return PolishResult(
        success=failed_batches == 0,
        segments=output_segments,
        warnings=warnings,
        success_batches=success_batches,
        failed_batches=failed_batches,
    )


def resolve_polish_batch_size(model_id: str) -> int:
    if settings.ollama_polish_batch_size:
        return max(1, settings.ollama_polish_batch_size)
    if model_id == "gemma3:1b":
        return 5
    if model_id in {"gemma4:12b", "gemma4:12b-it-qat"}:
        return 10
    return 8


def build_polish_prompt(segments: list[TranscriptSegment], profile_instruction: str | None = None) -> str:
    payload = [
        {
            "index": index,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        }
        for index, segment in enumerate(segments)
    ]
    example_input = [
        {"index": 0, "start": 0.0, "end": 1.2, "text": "hello world"},
        {"index": 1, "start": 1.2, "end": 2.5, "text": "this is test"},
    ]
    example_output = {
        "segments": [
            {"index": 0, "text": "Hello world."},
            {"index": 1, "text": "This is a test."},
        ]
    }
    return (
        "你是一个音频转录文本校对器。\n"
        f"{profile_instruction or '只修正明显的语音识别错误、标点、空格和断句。'}\n"
        "不要合并 segments。不要新增 segments。\n"
        "必须返回与输入完全相同数量的 segments。\n"
        "输出只允许包含 index 和 text。不要返回 start/end。\n"
        "index 必须原样返回。只允许修改 text。\n"
        "必须返回 JSON object，不要 markdown，不要解释。\n\n"
        "输出 JSON 结构必须是：\n"
        '{"segments":[{"index":0,"text":"..."}]}\n\n'
        "示例输入：\n"
        f"{json.dumps(example_input, ensure_ascii=False)}\n"
        "示例输出：\n"
        f"{json.dumps(example_output, ensure_ascii=False)}\n\n"
        "JSON Schema:\n"
        f"{json.dumps(polish_response_schema(), ensure_ascii=False)}\n\n"
        "当前输入：\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def polish_response_schema() -> dict[str, object]:
    return {
        "type": "object",
        "properties": {
            "segments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "text": {"type": "string"},
                    },
                    "required": ["index", "text"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["segments"],
        "additionalProperties": False,
    }


def parse_polish_response(raw: str, original: list[TranscriptSegment]) -> list[TranscriptSegment]:
    data = json.loads(extract_json(raw))
    if not isinstance(data, dict) or not isinstance(data.get("segments"), list):
        raise ValueError("Ollama polish 返回内容不是包含 segments 的 JSON 对象")
    data = data["segments"]
    if not isinstance(data, list):
        raise ValueError("Ollama polish 返回内容不是 JSON 数组")
    if len(data) != len(original):
        raise ValueError("Ollama polish 返回 segment 数量不一致")

    polished: list[TranscriptSegment] = []
    for expected_index, (item, source) in enumerate(zip(data, original, strict=True)):
        if not isinstance(item, dict):
            raise ValueError(f"Ollama polish 第 {expected_index} 项不是对象")
        if set(item) - {"index", "text"}:
            raise ValueError(f"Ollama polish 第 {expected_index} 项包含不允许的字段")
        returned_index = item.get("index", expected_index)
        if int(returned_index) != expected_index:
            raise ValueError(f"Ollama polish 第 {expected_index} 项 index 不一致")
        text_value = item.get("text")
        if not isinstance(text_value, str):
            raise ValueError(f"Ollama polish 第 {expected_index} 项 text 不是字符串")
        text = text_value.strip()
        if not text:
            raise ValueError(f"Ollama polish 第 {expected_index} 项 text 为空")
        polished.append(TranscriptSegment(start=source.start, end=source.end, text=text))
    return polished


def extract_json(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    if text.startswith("[") or text.startswith("{"):
        return text
    start_candidates = [position for position in [text.find("["), text.find("{")] if position >= 0]
    if not start_candidates:
        raise ValueError("Ollama polish 返回内容不包含 JSON")
    start = min(start_candidates)
    end = max(text.rfind("]"), text.rfind("}"))
    if end <= start:
        raise ValueError("Ollama polish 返回 JSON 不完整")
    return text[start : end + 1]


def publish_event(callback: Callable[[str, str], None] | None, message: str, level: str = "info") -> None:
    if callback:
        callback(message, level)


def publish_warning(callback: Callable[[str], None] | None, warning: str) -> None:
    if callback:
        callback(warning)
