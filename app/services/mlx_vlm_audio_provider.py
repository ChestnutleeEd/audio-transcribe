from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
from pathlib import Path

from app.config import settings
from app.schemas import MLXVlmAudioStatus
from app.services.audio_engine import AudioEngineResult
from app.services.exporters import TranscriptSegment
from app.services.media import ffmpeg_executable
from app.services.qwen_audio.audio_preprocess import audio_duration_seconds


def is_macos() -> bool:
    return platform.system().lower() == "darwin"


def is_apple_silicon() -> bool:
    return platform.machine().lower() in {"arm64", "aarch64"}


def ffmpeg_available() -> bool:
    executable = ffmpeg_executable()
    return bool(Path(executable).exists() or shutil.which(executable) or shutil.which("ffmpeg"))


def python_available(python_executable: str | None = None) -> bool:
    executable = (python_executable or settings.mlx_vlm_python).strip()
    return bool(executable and (Path(executable).exists() or shutil.which(executable)))


def configured_model(value: str | None = None) -> str:
    return (value or "").strip()


def is_local_model_path(value: str) -> bool:
    return bool(value and Path(value).expanduser().exists())


def local_model_type(model_path_or_repo: str) -> str | None:
    if not is_local_model_path(model_path_or_repo):
        return None
    config_path = Path(model_path_or_repo).expanduser() / "config.json"
    if not config_path.exists():
        return None
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    model_type = payload.get("model_type")
    return str(model_type).strip().lower() if model_type else None


def is_mlx_vlm_audio_model(model_path_or_repo: str | None) -> bool:
    configured = configured_model(model_path_or_repo)
    if not configured:
        return False
    model_type = local_model_type(configured)
    if model_type:
        return model_type == "gemma4"
    text = configured.lower()
    return "gemma4" in text or "mlx-vlm" in text or "mlx_vlm" in text


def dependency_available(python_executable: str | None = None) -> bool:
    executable = (python_executable or settings.mlx_vlm_python).strip()
    if not python_available(executable):
        return False
    try:
        result = subprocess.run(
            [executable, "-c", "import importlib.util; raise SystemExit(0 if importlib.util.find_spec('mlx_vlm') else 1)"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return result.returncode == 0


def mlx_vlm_audio_status(model_path_or_repo: str | None = None) -> MLXVlmAudioStatus:
    configured = configured_model(model_path_or_repo)
    platform_supported = is_macos() and is_apple_silicon()
    py_available = python_available()
    dependency_installed = dependency_available() if py_available else False
    model_configured = bool(configured)
    model_type = local_model_type(configured) if configured else None
    ffmpeg_ok = ffmpeg_available()
    available = platform_supported and py_available and dependency_installed and model_configured and ffmpeg_ok

    reason = None
    hint = None
    if not platform_supported:
        reason = "当前平台不是 macOS Apple Silicon。"
        hint = "Gemma4 MLX 音频模型主要适用于 M 系列 Mac。"
    elif not py_available:
        reason = "未找到 mlx_vlm Python 解释器。"
        hint = "请先运行项目安装脚本创建 .venv；如需自定义解释器，可设置 AUDIO_TRANSCRIBE_MLX_VLM_PYTHON。"
    elif not dependency_installed:
        reason = "该 Python 环境未检测到 mlx_vlm。"
        hint = "请运行项目安装脚本安装 requirements.txt，或在当前 .venv 中安装 mlx-vlm。"
    elif not model_configured:
        reason = "未配置 Gemma4 MLX 音频模型路径。"
        hint = "请选择或填写本地 gemma4-e4b-qat-4bit 模型目录。"
    elif not ffmpeg_ok:
        reason = "FFmpeg 不可用。"
        hint = "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。"
    elif is_local_model_path(configured) and model_type not in {"gemma4", None}:
        reason = f"当前 mlx-vlm 音频入口未确认支持 {model_type} 模型。"
        hint = "请选择 Gemma4 MLX Audio/Text 模型，Qwen2-Audio 请继续使用 MLX Audio 管线。"
        available = False
    elif not is_local_model_path(configured):
        reason = "配置的 Gemma4 MLX 模型路径不存在。"
        hint = "请填写已下载的本地模型目录。"
        available = False

    return MLXVlmAudioStatus(
        available=available,
        platform_supported=platform_supported,
        dependency_installed=dependency_installed,
        model_configured=model_configured,
        python_available=py_available,
        ffmpeg_available=ffmpeg_ok,
        is_macos=is_macos(),
        is_apple_silicon=is_apple_silicon(),
        os=platform.system() or "unknown",
        arch=platform.machine() or "unknown",
        python_executable=settings.mlx_vlm_python,
        model_path_or_repo=configured,
        model_type=model_type,
        max_tokens=settings.mlx_vlm_max_tokens,
        reason=reason,
        hint=hint,
    )


def parse_mlx_vlm_generate_output(stdout: str) -> str:
    parts = stdout.split("==========")
    if len(parts) >= 3:
        body = parts[1]
        marker = "<|turn>model"
        if marker in body:
            body = body.split(marker, 1)[1]
        return body.strip()

    lines = []
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith(("Files:", "Prompt:", "Generation:", "Peak memory:")):
            continue
        lines.append(line)
    return "\n".join(lines).strip()


def clean_transcript_text(text: str) -> str:
    value = re.sub(r"\s+", " ", text or "").strip()
    return value.strip(" \n\t`")


def transcribe_with_mlx_vlm_audio(
    audio_path: Path,
    model_path_or_repo: str,
    language: str | None = None,
) -> AudioEngineResult:
    del language
    status = mlx_vlm_audio_status(model_path_or_repo)
    if not status.available:
        raise RuntimeError(status.reason or "Gemma4 MLX VLM Audio 前置条件未满足。")

    command = [
        status.python_executable,
        "-m",
        "mlx_vlm.generate",
        "--model",
        model_path_or_repo,
        "--audio",
        str(audio_path),
        "--prompt",
        settings.mlx_vlm_prompt,
        "--max-tokens",
        str(settings.mlx_vlm_max_tokens),
    ]
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=settings.mlx_vlm_timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"Gemma4 MLX VLM Audio 转录超时：{exc}") from exc
    except OSError as exc:
        raise RuntimeError(f"无法启动 Gemma4 MLX VLM Audio：{exc}") from exc

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Gemma4 MLX VLM Audio 转录失败：{detail}")

    transcript = clean_transcript_text(parse_mlx_vlm_generate_output(result.stdout))
    if not transcript:
        detail = (result.stderr or result.stdout or "").strip()
        raise RuntimeError(f"Gemma4 MLX VLM Audio 未返回转写文本：{detail}")

    duration = audio_duration_seconds(audio_path)
    segments = [TranscriptSegment(start=0.0, end=round(duration, 3), text=transcript)]
    metadata = {
        "engine": "mlx-vlm-audio",
        "backend": "mlx-vlm",
        "model": model_path_or_repo,
        "python": status.python_executable,
        "prompt": settings.mlx_vlm_prompt,
        "maxTokens": settings.mlx_vlm_max_tokens,
    }
    return AudioEngineResult.from_segments(
        segments=segments,
        engine_name="mlx-vlm-audio",
        model_label=f"{Path(model_path_or_repo).name or model_path_or_repo}（MLX VLM Audio）",
        metadata=metadata,
    )
