from __future__ import annotations

import importlib.util
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.config import OLLAMA_POLISH_MODELS, SUPPORTED_MODELS
from app.schemas import HealthCheckItem, HealthCheckStatus
from app.services.media import ffmpeg_executable
from app.services.mlx_whisper_provider import mlx_whisper_status
from app.services.model_manager import model_status
from app.services.ollama_model_manager import ollama_status


def module_available(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def health_check() -> HealthCheckStatus:
    items: list[HealthCheckItem] = []
    model = model_status()
    ollama = ollama_status()

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
            status="success" if module_available("faster_whisper") else "error",
            message="faster-whisper 可导入。" if module_available("faster_whisper") else "未检测到 faster-whisper Python 包。",
            suggestion=None if module_available("faster_whisper") else "激活虚拟环境后执行 pip install -r requirements.txt。",
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
    items.append(
        HealthCheckItem(
            id="whisper_models",
            label="Whisper 模型列表",
            status="success" if any(item.available for item in model.models) else "warning",
            message=", ".join(f"{item.id}{' 已就绪' if item.available else ' 未下载'}" for item in model.models)
            or "未读取到模型列表。",
            suggestion=None
            if any(item.available for item in model.models)
            else "在页面选择模型并确认下载，或手动把模型文件放入 models/ 对应目录。",
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
            id="ollama_models",
            label="Ollama 已安装模型",
            status="success" if ollama.local_models else "warning",
            message=", ".join(ollama.local_models) if ollama.local_models else "未读取到 Ollama 本地模型。",
            suggestion=None if ollama.local_models else "执行 ollama list 检查本地模型。",
        )
    )
    local = set(ollama.local_models)
    for definition in OLLAMA_POLISH_MODELS:
        exists = any(name == definition.id or name.startswith(f"{definition.id}:") for name in local)
        items.append(
            HealthCheckItem(
                id=f"ollama_model_{definition.id}",
                label=f"{definition.id} 模型",
                status="success" if exists else "warning",
                message=f"已检测到 {definition.id}" if exists else f"未检测到 {definition.id}",
                suggestion=None if exists else f"需要时在应用外手动安装 {definition.id}，或切换到已安装模型。",
            )
        )

    supported = ", ".join(item.id for item in SUPPORTED_MODELS)
    items.append(
        HealthCheckItem(
            id="supported_whisper_models",
            label="可选 faster-whisper 模型",
            status="success",
            message=supported,
        )
    )
    return HealthCheckStatus(checked_at=datetime.now(timezone.utc).isoformat(), items=items)
