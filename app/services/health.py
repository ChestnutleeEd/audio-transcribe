from __future__ import annotations

import importlib.util
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.schemas import HealthCheckItem, HealthCheckStatus
from app.services.media import ffmpeg_executable
from app.services.mlx_whisper_provider import mlx_whisper_status
from app.services.model_registry import model_registry
from app.services.ollama_model_manager import ollama_status
from app.services.qwen_audio import qwen_audio_status


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def health_check() -> HealthCheckStatus:
    items: list[HealthCheckItem] = []
    ollama = ollama_status()
    faster_whisper_available = module_available("faster_whisper")

    items.append(
        HealthCheckItem(
            id="python",
            label="后端服务 / Python",
            status="success",
            message=f"Python {sys.version.split()[0]}，FastAPI 服务正在运行。",
        )
    )
    items.append(
        HealthCheckItem(
            id="faster_whisper",
            label="faster-whisper",
            status="success" if faster_whisper_available else "error",
            message="faster-whisper 可导入。" if faster_whisper_available else "未检测到 faster-whisper Python 包。",
            suggestion=None if faster_whisper_available else "激活虚拟环境后执行 pip install -r requirements.txt。",
        )
    )
    mlx_status = mlx_whisper_status()
    items.append(
        HealthCheckItem(
            id="mlx_whisper",
            label="MLX Whisper",
            status="success" if mlx_status.available else "warning",
            message=mlx_status.reason or "MLX Whisper 可用。",
            suggestion=mlx_status.hint,
        )
    )
    qwen_status = qwen_audio_status()
    items.append(
        HealthCheckItem(
            id="qwen_audio",
            label="MLX Audio",
            status="success" if qwen_status.available else "warning",
            message=qwen_status.reason or "MLX Audio 可用。",
            suggestion=qwen_status.hint,
        )
    )
    registry = model_registry()
    audio_count = sum(1 for item in registry.models if item.capabilities.audio and item.metadata.status == "available")
    text_count = sum(1 for item in registry.models if item.capabilities.text and item.metadata.status == "available")
    items.append(
        HealthCheckItem(
            id="model_registry",
            label="统一模型池",
            status="success" if registry.models else "warning",
            message=f"检测到 {len(registry.models)} 个模型；Audio {audio_count} 个，Text {text_count} 个。",
            suggestion=None if registry.models else "可启动本地 provider，或在页面注册自定义模型路径。",
        )
    )
    ffmpeg_path = ffmpeg_executable()
    ffmpeg_ok = bool(Path(ffmpeg_path).exists() or shutil.which(ffmpeg_path) or shutil.which("ffmpeg"))
    items.append(
        HealthCheckItem(
            id="ffmpeg",
            label="FFmpeg",
            status="success" if ffmpeg_ok else "error",
            message=f"FFmpeg 路径：{ffmpeg_path}" if ffmpeg_ok else "未检测到 FFmpeg。",
            suggestion=None if ffmpeg_ok else "安装 FFmpeg，或设置 AUDIO_TRANSCRIBE_FFMPEG 指向可执行文件。",
        )
    )
    items.append(
        HealthCheckItem(
            id="ollama",
            label="Ollama 服务",
            status="success" if ollama.available else "warning",
            message=ollama.message,
            suggestion=None if ollama.available else "启动 Ollama 桌面应用，或执行 ollama serve。",
        )
    )
    items.append(
        HealthCheckItem(
            id="api_server",
            label="API server status",
            status="success",
            message="FastAPI API server 可响应。",
        )
    )
    return HealthCheckStatus(checked_at=datetime.now(timezone.utc).isoformat(), items=items)
