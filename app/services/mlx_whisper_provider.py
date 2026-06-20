from __future__ import annotations

import importlib.util
import os
import platform
import shutil
from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas import MLXWhisperStatus
from app.services.exporters import TranscriptSegment
from app.services.media import ffmpeg_executable


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def is_apple_silicon() -> bool:
    return platform.machine().lower() in {"arm64", "aarch64"}


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ffmpeg_available() -> bool:
    executable = ffmpeg_executable()
    return bool(Path(executable).exists() or shutil.which(executable) or shutil.which("ffmpeg"))


def is_local_model_path(value: str) -> bool:
    if not value:
        return False
    candidate = Path(value).expanduser()
    return candidate.exists()


def looks_like_repo_id(value: str) -> bool:
    value = value.strip()
    return "/" in value and not value.startswith(("/", ".", "~")) and not Path(value).exists()


def configured_model(value: str | None = None) -> str:
    return (value if value is not None else settings.mlx_whisper_model_path_or_repo).strip()


def mlx_whisper_status(model_path_or_repo: str | None = None) -> MLXWhisperStatus:
    configured = configured_model(model_path_or_repo)
    platform_supported = is_macos() and is_apple_silicon()
    dependency_installed = module_available("mlx_whisper")
    model_configured = bool(configured)
    ffmpeg_ok = ffmpeg_available()
    available = platform_supported and dependency_installed and model_configured and ffmpeg_ok

    reason = None
    hint = None
    if not platform_supported:
        reason = "当前平台不是 macOS Apple Silicon。"
        hint = "MLX Whisper 主要适用于 M 系列 Mac；其他平台建议使用 faster-whisper。"
    elif not dependency_installed:
        reason = "未检测到 mlx-whisper Python 包。"
        hint = "请在项目 Python 环境中自行安装 mlx-whisper，本项目不会自动安装。"
    elif not model_configured:
        reason = "未配置 MLX Whisper 模型路径或 repo id。"
        hint = "请填写本地 MLX 模型目录；repo id 仅在本地缓存已存在时可用，本项目不会自动下载模型。"
    elif not ffmpeg_ok:
        reason = "FFmpeg 不可用。"
        hint = "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。"
    elif looks_like_repo_id(configured):
        hint = "检测到 Hugging Face repo id；转录时将启用离线模式，避免自动下载。请确认模型已预先缓存。"
    elif not is_local_model_path(configured):
        reason = "配置的本地 MLX 模型路径不存在。"
        hint = "请确认路径存在，或填写已预先缓存的 Hugging Face repo id。"
        available = False

    return MLXWhisperStatus(
        available=available,
        platform_supported=platform_supported,
        dependency_installed=dependency_installed,
        model_configured=model_configured,
        ffmpeg_available=ffmpeg_ok,
        is_macos=is_macos(),
        is_apple_silicon=is_apple_silicon(),
        os=platform.system() or "unknown",
        arch=platform.machine() or "unknown",
        model_path_or_repo=configured,
        default_model_label=settings.mlx_whisper_default_model_label,
        language=settings.mlx_whisper_language,
        reason=reason,
        hint=hint,
    )


def _segment_from_mapping(segment: dict[str, Any]) -> TranscriptSegment | None:
    text = str(segment.get("text") or "").strip()
    if not text:
        return None
    start = float(segment.get("start") or 0)
    end = float(segment.get("end") or start)
    return TranscriptSegment(start=start, end=end, text=text)


def transcribe_with_mlx_whisper(
    audio_path: Path,
    model_path_or_repo: str,
    language: str | None,
) -> list[TranscriptSegment]:
    status = mlx_whisper_status(model_path_or_repo)
    if not status.platform_supported:
        raise RuntimeError("MLX Whisper 主要适用于 macOS Apple Silicon，当前平台不适配。")
    if not status.dependency_installed:
        raise RuntimeError("未安装 mlx-whisper。请自行安装依赖后重试，本项目不会自动安装。")
    if not status.model_configured:
        raise RuntimeError("未配置 MLX Whisper 模型路径或 repo id。")
    if not status.ffmpeg_available:
        raise RuntimeError("FFmpeg 不可用，无法执行 MLX Whisper 转录。")
    if status.reason and not looks_like_repo_id(model_path_or_repo):
        raise RuntimeError(status.reason)

    import mlx_whisper

    whisper_language = None if language in {None, "", "auto"} else language
    previous_offline = os.environ.get("HF_HUB_OFFLINE")
    if looks_like_repo_id(model_path_or_repo):
        os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        result = mlx_whisper.transcribe(
            str(audio_path),
            path_or_hf_repo=model_path_or_repo,
            language=whisper_language,
            task="transcribe",
        )
    except Exception as exc:
        raise RuntimeError(f"MLX Whisper 转录失败：{exc}") from exc
    finally:
        if previous_offline is None:
            os.environ.pop("HF_HUB_OFFLINE", None)
        else:
            os.environ["HF_HUB_OFFLINE"] = previous_offline

    segments = []
    for segment in result.get("segments") or []:
        parsed = _segment_from_mapping(segment)
        if parsed:
            segments.append(parsed)
    if segments:
        return segments

    text = str(result.get("text") or "").strip()
    if text:
        return [TranscriptSegment(start=0.0, end=0.0, text=text)]
    return []
