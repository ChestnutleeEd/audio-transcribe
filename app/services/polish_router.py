from __future__ import annotations

from dataclasses import dataclass

from app.config import settings
from app.schemas import UnifiedModel
from app.services.exporters import TranscriptSegment
from app.services.model_registry import model_registry
from app.services.ollama_model_manager import check_model as check_ollama_model
from app.services.ollama_provider import PolishResult, polish_segments as polish_with_ollama
from app.services.qwen_audio.qwen_infer import qwen_audio_status
from app.services.qwen_audio_polish import polish_segments_with_qwen_audio


@dataclass(frozen=True)
class PolishModelRef:
    provider: str
    model_id: str
    path_or_id: str
    model: UnifiedModel | None = None

    @property
    def is_ollama(self) -> bool:
        return self.provider == "ollama"

    @property
    def is_mlx_audio(self) -> bool:
        text = f"{self.model_id} {self.path_or_id}".lower()
        return self.provider in {"mlx", "custom", "huggingface"} and ("qwen2-audio" in text or "audio" in text)


def resolve_polish_model(model_id: str | None) -> PolishModelRef | None:
    value = (model_id or "").strip()
    if not value:
        return None

    registry = model_registry()
    for model in registry.models:
        if model.id == value or model.path_or_id == value:
            return PolishModelRef(
                provider=model.provider,
                model_id=model.id,
                path_or_id=model.path_or_id,
                model=model,
            )

    return PolishModelRef(provider="ollama", model_id=value, path_or_id=value)


def validate_polish_model(model_ref: PolishModelRef) -> None:
    if settings.mock_mode:
        return
    if model_ref.is_ollama:
        check = check_ollama_model(model_ref.path_or_id)
        if not check.service_available:
            raise RuntimeError("Ollama 服务不可用，请先启动 Ollama。")
        if not check.available:
            raise RuntimeError(f"未检测到 {check.model_id}，请选择已安装模型或在应用外手动安装。")
        return

    if model_ref.is_mlx_audio:
        status = qwen_audio_status(model_ref.path_or_id)
        if not status.available:
            raise RuntimeError(status.reason or "MLX Audio 文本整理模型不可用")
        return

    raise RuntimeError(f"当前暂不支持使用 {model_ref.provider} 模型执行文本整理：{model_ref.path_or_id}")


def polish_segments(
    segments: list[TranscriptSegment],
    model_ref: PolishModelRef,
    profile_instruction: str | None,
    **callbacks,
) -> PolishResult:
    if model_ref.is_ollama or settings.mock_mode:
        return polish_with_ollama(segments, model_ref.path_or_id, profile_instruction, **callbacks)
    if model_ref.is_mlx_audio:
        return polish_segments_with_qwen_audio(segments, model_ref.path_or_id, profile_instruction, **callbacks)
    raise RuntimeError(f"当前暂不支持使用 {model_ref.provider} 模型执行文本整理：{model_ref.path_or_id}")
