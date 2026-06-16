from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.config import settings
from app.services.exporters import TranscriptSegment
from app.services.ollama_client import OllamaClient, OllamaError


DIRECT_AUDIO_UNSUPPORTED = "Current Ollama API does not support direct audio input for this model."


@dataclass(frozen=True)
class OllamaTranscriptionResult:
    segments: list[TranscriptSegment]
    warnings: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolishResult:
    success: bool
    segments: list[TranscriptSegment]
    warning: str | None = None


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
                    text=f"这是 {model_id} mock direct audio transcription 的完整转录结果。",
                )
            ],
            warnings=["Gemma 4 direct audio transcription does not provide precise segment timestamps."],
        )
    _ = (audio_path, model_id, audio_duration)
    raise OllamaError(DIRECT_AUDIO_UNSUPPORTED)


def polish_segments(
    segments: list[TranscriptSegment],
    model_id: str,
    client: OllamaClient | None = None,
) -> PolishResult:
    if not segments:
        return PolishResult(success=True, segments=segments)
    if settings.mock_mode:
        if settings.mock_polish_fail:
            return PolishResult(
                success=False,
                segments=segments,
                warning="Polish failed: mock polish failure. Returned original transcription.",
            )
        return PolishResult(
            success=True,
            segments=[
                TranscriptSegment(start=segment.start, end=segment.end, text=f"{segment.text}（mock polished）")
                for segment in segments
            ],
        )

    ollama = client or OllamaClient()
    prompt = build_polish_prompt(segments)
    try:
        result = ollama.generate_text(model_id, prompt, response_format=polish_response_schema())
        polished = parse_polish_response(result.response, segments)
    except Exception as exc:
        return PolishResult(
            success=False,
            segments=segments,
            warning=f"Polish failed: {exc}. Returned original transcription.",
        )
    return PolishResult(success=True, segments=polished)


def build_polish_prompt(segments: list[TranscriptSegment]) -> str:
    payload = [
        {
            "index": index,
            "start": segment.start,
            "end": segment.end,
            "text": segment.text,
        }
        for index, segment in enumerate(segments)
    ]
    return (
        "你是一个音频转录文本校对器。请只修正明显的语音识别错误、标点、空格和断句。"
        "不要总结，不要翻译，不要扩写，不要删除信息。"
        "输入是 JSON 数组，每个元素包含 index/start/end/text。"
        "请返回对象 {\"segments\": [...]}，segments 长度必须相同。"
        "只允许修改 text 字段，index/start/end 必须原样返回。"
        "只返回 JSON，不要返回 Markdown，不要解释。\n\n"
        f"JSON Schema:\n{json.dumps(polish_response_schema(), ensure_ascii=False)}\n\n"
        f"{json.dumps(payload, ensure_ascii=False)}"
    )


def polish_response_schema() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "segments": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "index": {"type": "integer"},
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "text": {"type": "string"},
                    },
                    "required": ["index", "start", "end", "text"],
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
    for index, (item, source) in enumerate(zip(data, original, strict=True)):
        if not isinstance(item, dict):
            raise ValueError(f"Ollama polish 第 {index} 项不是对象")
        if set(item) - {"index", "start", "end", "text"}:
            raise ValueError(f"Ollama polish 第 {index} 项包含不允许的字段")
        returned_index = item.get("index", index)
        if int(returned_index) != index:
            raise ValueError(f"Ollama polish 第 {index} 项 index 不一致")
        if not same_number(item.get("start"), source.start) or not same_number(item.get("end"), source.end):
            raise ValueError(f"Ollama polish 第 {index} 项时间戳被修改")
        text = str(item.get("text") or "").strip()
        if not text:
            raise ValueError(f"Ollama polish 第 {index} 项 text 为空")
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


def same_number(value: Any, expected: float) -> bool:
    try:
        return abs(float(value) - float(expected)) < 0.001
    except (TypeError, ValueError):
        return False
