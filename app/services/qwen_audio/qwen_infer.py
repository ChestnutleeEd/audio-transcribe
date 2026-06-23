from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import re
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
    model_type: str | None = None
    model_supported: bool | None = None
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


def repo_cached_locally(value: str) -> bool:
    if not looks_like_repo_id(value):
        return False
    try:
        from huggingface_hub import snapshot_download

        snapshot_download(value, local_files_only=True)
        return True
    except Exception:
        return False


def configured_model(value: str | None = None) -> str:
    return (value if value is not None else settings.qwen_audio_model_path_or_repo).strip()


def local_config_path(model_path_or_repo: str) -> Path | None:
    if not is_local_model_path(model_path_or_repo):
        return None
    config_path = Path(model_path_or_repo).expanduser() / "config.json"
    return config_path if config_path.exists() else None


def local_model_type(model_path_or_repo: str) -> str | None:
    config_path = local_config_path(model_path_or_repo)
    if not config_path:
        return None
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    model_type = payload.get("model_type")
    return str(model_type).strip().lower() if model_type else None


def qwen_audio_model_supported(model_path_or_repo: str) -> bool | None:
    model_type = local_model_type(model_path_or_repo)
    if model_type is not None:
        return model_type == "qwen2_audio"
    value = model_path_or_repo.strip().lower()
    if not value:
        return None
    if "qwen2-audio" in value or "qwen_audio" in value or "qwen-audio" in value:
        return True
    if "gemma" in value:
        return False
    return None


def clean_qwen_transcript_text(text: str) -> str:
    value = re.sub(r"\s+", " ", text or "").strip()
    wrappers = (
        r"^(?:The\s+)?original content of this audio is\s*:\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
        r"^The audio says\s*:\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
        r"^The transcript is\s*:\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
        r"^Transcription\s*:\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
        r"^原始音频内容[是为]?\s*[:：]\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
        r"^这段音频的内容[是为]?\s*[:：]?\s*['\"“”‘’]?(?P<body>.+?)['\"“”‘’]?[。.!！]?$",
    )
    for pattern in wrappers:
        match = re.match(pattern, value, flags=re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group("body").strip()
            break
    return value.strip(" \n\t`'\"“”‘’")


def qwen_audio_status(model_path_or_repo: str | None = None) -> QwenAudioStatus:
    configured = configured_model(model_path_or_repo)
    platform_supported = is_macos() and is_apple_silicon()
    dependency_installed = module_available("mlx_audio")
    model_configured = bool(configured)
    ffmpeg_ok = ffmpeg_available()
    offline_mode = not settings.qwen_audio_allow_download
    available = platform_supported and dependency_installed and model_configured and ffmpeg_ok
    model_type = local_model_type(configured) if configured else None
    model_supported = qwen_audio_model_supported(configured) if configured else None

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
    elif model_supported is False:
        label = model_type or Path(configured).name or configured
        reason = f"当前 MLX Audio STT 后端不支持 {label} 模型。"
        hint = "Local Audio LLM 的 MLX Audio 转录管线目前只支持 Qwen2-Audio；Gemma 音频模型暂未接入可用的本地音频转录适配器。"
        available = False
    elif not ffmpeg_ok:
        reason = "FFmpeg 不可用。"
        hint = "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。"
    elif looks_like_repo_id(configured):
        if not settings.qwen_audio_allow_download and not repo_cached_locally(configured):
            reason = "Qwen2-Audio repo id 未在本地缓存中找到。"
            hint = (
                "请先在应用外执行 huggingface-cli download 下载模型，或填写已下载的本地模型目录。"
                "本项目默认不会自动下载模型。"
            )
            available = False
        else:
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
        model_type=model_type,
        model_supported=model_supported,
        reason=reason,
        hint=hint,
    )


@contextmanager
def qwen_offline_env(model_path_or_repo: str) -> Iterator[None]:
    del model_path_or_repo
    previous = os.environ.get("HF_HUB_OFFLINE")
    if not settings.qwen_audio_allow_download:
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


class QwenAudioTranscriber:
    """本地 Qwen2-Audio MLX 推理封装；不负责下载模型。"""

    def __init__(self, model_path_or_repo: str | None = None, prompt: str | None = None) -> None:
        self.model_path_or_repo = configured_model(model_path_or_repo)
        self.prompt = prompt or settings.qwen_audio_prompt
        self._validate_available()
        self.model = load_qwen_audio_model(self.model_path_or_repo)

    def _validate_available(self) -> None:
        status = qwen_audio_status(self.model_path_or_repo)
        if not status.platform_supported:
            raise RuntimeError("Qwen2-Audio MLX 后端主要适用于 macOS Apple Silicon，当前平台不适配。")
        if not status.dependency_installed:
            raise RuntimeError("未安装 mlx-audio。请自行安装依赖后重试，本项目不会自动安装。")
        if not status.model_configured:
            raise RuntimeError("未配置 Qwen2-Audio 模型路径或 repo id。")
        if not status.ffmpeg_available:
            raise RuntimeError("FFmpeg 不可用，无法执行 Qwen2-Audio 推理。")
        if status.reason:
            raise RuntimeError(status.reason)

    def generate(self, audio_path: Path | str, prompt: str | None = None) -> str:
        active_prompt = prompt or self.prompt
        with qwen_offline_env(self.model_path_or_repo):
            result = self.model.generate(str(audio_path), prompt=active_prompt)
        text = getattr(result, "text", None)
        if text is None:
            text = result.get("text") if isinstance(result, dict) else str(result)
        return clean_qwen_transcript_text(str(text or ""))

    def transcribe_chunk(self, audio_path: Path | str, prompt: str | None = None) -> str:
        return self.generate(audio_path, prompt=prompt)


def infer_chunk(
    audio_path: Path,
    model_path_or_repo: str | None = None,
    prompt: str | None = None,
) -> str:
    return QwenAudioTranscriber(model_path_or_repo=model_path_or_repo, prompt=prompt).transcribe_chunk(audio_path)


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
