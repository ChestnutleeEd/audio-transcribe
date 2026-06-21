from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
from contextlib import contextmanager
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from app.config import settings
from app.services.media import ffmpeg_executable

QWEN_AUDIO_MODEL_ID = "mlx-community/Qwen2-Audio-7B-Instruct-4bit"
QWEN_AUDIO_MODEL_LABEL = "Qwen2-Audio-7B-Instruct-4bit"
QWEN_AUDIO_BACKEND = "mlx-audio"


@dataclass(frozen=True)
class QwenAudioStatus:
    engine: str
    available: bool
    platform_supported: bool
    dependency_installed: bool
    model_configured: bool
    ffmpeg_available: bool
    offline_mode: bool
    is_macos: bool
    is_apple_silicon: bool
    os: str
    arch: str
    model_path_or_repo: str
    default_model_label: str
    reason: str | None = None
    hint: str | None = None


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def is_apple_silicon() -> bool:
    return platform.machine().lower() in {"arm64", "aarch64"}


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def ffmpeg_available() -> bool:
    executable = ffmpeg_executable()
    return bool(Path(executable).exists() or shutil.which(executable) or shutil.which("ffmpeg"))


def looks_like_repo_id(value: str) -> bool:
    value = value.strip()
    return "/" in value and not value.startswith(("/", ".", "~")) and not Path(value).expanduser().exists()


def is_local_model_path(value: str) -> bool:
    return bool(value and Path(value).expanduser().exists())


def configured_model(value: str | None = None) -> str:
    return (value if value is not None else settings.qwen_audio_model_path_or_repo).strip()


def qwen_audio_status(model_path_or_repo: str | None = None) -> QwenAudioStatus:
    configured = configured_model(model_path_or_repo)
    platform_supported = is_macos() and is_apple_silicon()
    dependency_installed = module_available("mlx_audio")
    model_configured = bool(configured)
    ffmpeg_ok = ffmpeg_available()
    offline_mode = looks_like_repo_id(configured) and not settings.qwen_audio_allow_download
    available = platform_supported and dependency_installed and model_configured and ffmpeg_ok

    reason = None
    hint = None
    if not platform_supported:
        reason = "当前平台不是 macOS Apple Silicon。"
        hint = "Qwen2-Audio MLX 后端主要适用于 M 系列 Mac；其他平台请使用 Whisper。"
    elif not dependency_installed:
        reason = "未检测到 mlx-audio Python 包。"
        hint = "请在项目 Python 环境中自行安装 mlx-audio；本项目不会自动安装或调用云服务。"
    elif not model_configured:
        reason = "未配置 Qwen2-Audio 模型路径或 repo id。"
        hint = f"默认模型是 {QWEN_AUDIO_MODEL_ID}，建议先下载到本地目录再填写路径。"
    elif not ffmpeg_ok:
        reason = "FFmpeg 不可用。"
        hint = "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。"
    elif looks_like_repo_id(configured):
        hint = (
            "检测到 Hugging Face repo id；默认启用离线模式，避免自动下载。"
            "如需首次下载，请先在应用外执行 huggingface-cli download，或显式设置 AUDIO_TRANSCRIBE_QWEN_AUDIO_ALLOW_DOWNLOAD=1。"
        )
    elif not is_local_model_path(configured):
        reason = "配置的 Qwen2-Audio 本地模型路径不存在。"
        hint = "请填写已下载的本地模型目录，或填写已预先缓存的 repo id。"
        available = False

    return QwenAudioStatus(
        engine="qwen-audio",
        available=available,
        platform_supported=platform_supported,
        dependency_installed=dependency_installed,
        model_configured=model_configured,
        ffmpeg_available=ffmpeg_ok,
        offline_mode=offline_mode,
        is_macos=is_macos(),
        is_apple_silicon=is_apple_silicon(),
        os=platform.system() or "unknown",
        arch=platform.machine() or "unknown",
        model_path_or_repo=configured,
        default_model_label=settings.qwen_audio_default_model_label,
        reason=reason,
        hint=hint,
    )


@contextmanager
def qwen_offline_env(model_path_or_repo: str) -> Iterator[None]:
    previous = os.environ.get("HF_HUB_OFFLINE")
    if looks_like_repo_id(model_path_or_repo) and not settings.qwen_audio_allow_download:
        os.environ["HF_HUB_OFFLINE"] = "1"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop("HF_HUB_OFFLINE", None)
        else:
            os.environ["HF_HUB_OFFLINE"] = previous


@lru_cache(maxsize=2)
def load_qwen_audio_model(model_path_or_repo: str):
    with qwen_offline_env(model_path_or_repo):
        from mlx_audio.stt.utils import load_model

        return load_model(model_path_or_repo)


def infer_chunk(
    audio_path: Path,
    model_path_or_repo: str | None = None,
    prompt: str | None = None,
) -> str:
    configured = configured_model(model_path_or_repo)
    status = qwen_audio_status(configured)
    if not status.platform_supported:
        raise RuntimeError("Qwen2-Audio MLX 后端主要适用于 macOS Apple Silicon，当前平台不适配。")
    if not status.dependency_installed:
        raise RuntimeError("未安装 mlx-audio。请自行安装依赖后重试，本项目不会自动安装。")
    if not status.model_configured:
        raise RuntimeError("未配置 Qwen2-Audio 模型路径或 repo id。")
    if not status.ffmpeg_available:
        raise RuntimeError("FFmpeg 不可用，无法执行 Qwen2-Audio 推理。")
    if status.reason and not looks_like_repo_id(configured):
        raise RuntimeError(status.reason)

    model = load_qwen_audio_model(configured)
    active_prompt = prompt or settings.qwen_audio_prompt
    with qwen_offline_env(configured):
        result = model.generate(str(audio_path), prompt=active_prompt)
    text = getattr(result, "text", None)
    if text is None:
        text = result.get("text") if isinstance(result, dict) else str(result)
    return str(text or "").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="本地 Qwen2-Audio 单 chunk 推理。")
    parser.add_argument("audio_path", help="待分析的 16kHz 单声道音频 chunk 路径。")
    parser.add_argument("--model", default=settings.qwen_audio_model_path_or_repo, help="本地模型目录或已缓存 repo id。")
    parser.add_argument("--prompt", default=settings.qwen_audio_prompt, help="音频理解提示词。")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出结果。")
    args = parser.parse_args()

    text = infer_chunk(Path(args.audio_path), args.model, args.prompt)
    if args.json:
        print(json.dumps({"audio_path": args.audio_path, "model": args.model, "backend": QWEN_AUDIO_BACKEND, "text": text}, ensure_ascii=False, indent=2))
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
