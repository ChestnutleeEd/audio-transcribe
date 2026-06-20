from __future__ import annotations

from dataclasses import dataclass
import time
from threading import Lock

from app.config import OLLAMA_POLISH_MODELS, OLLAMA_TRANSCRIPTION_MODELS, settings
from app.schemas import (
    ModelDownloadState,
    OllamaModelCheck,
    OllamaModelOption,
    OllamaPreflightStatus,
    OllamaPullStatus,
    OllamaServiceStatus,
)
from app.services.ollama_client import OllamaClient, OllamaError, OllamaPullCanceled, OllamaUnavailableError


@dataclass
class OllamaPullTracker:
    model_id: str
    state: ModelDownloadState = ModelDownloadState.idle
    message: str = "模型尚未检测"
    error: str | None = None
    cancel_requested: bool = False
    progress: int = 0
    completed_bytes: int | None = None
    total_bytes: int | None = None
    progress_label: str | None = None


trackers: dict[str, OllamaPullTracker] = {}
tracker_lock = Lock()


def client() -> OllamaClient:
    return OllamaClient(settings.ollama_base_url)


def get_tracker(model_id: str) -> OllamaPullTracker:
    if model_id not in trackers:
        trackers[model_id] = OllamaPullTracker(model_id=model_id)
    return trackers[model_id]


def model_option(definition, local_models: list[str]) -> OllamaModelOption:
    return OllamaModelOption(
        id=definition.id,
        label=definition.label,
        role=definition.role,
        experimental=definition.experimental,
        default=definition.default,
        available=model_id_in_list(definition.id, local_models),
    )


def ollama_status() -> OllamaServiceStatus:
    if settings.mock_mode:
        local_models = ["gemma4:12b-it-qat", "gemma3:1b"]
        return OllamaServiceStatus(
            available=True,
            base_url=settings.ollama_base_url,
            mock_mode=True,
            version="mock",
            message="Mock 模式：不会调用真实模型",
            local_models=local_models,
            transcription_models=[model_option(model, local_models) for model in OLLAMA_TRANSCRIPTION_MODELS],
            polish_models=[model_option(model, local_models) for model in OLLAMA_POLISH_MODELS],
        )

    ollama = client()
    try:
        version_payload = ollama.version()
        local_models = ollama.list_models()
    except OllamaUnavailableError as exc:
        return OllamaServiceStatus(
            available=False,
            base_url=settings.ollama_base_url,
            mock_mode=False,
            message="Ollama 服务不可用，请先启动 Ollama。",
            error=str(exc),
            transcription_models=[model_option(model, []) for model in OLLAMA_TRANSCRIPTION_MODELS],
            polish_models=[model_option(model, []) for model in OLLAMA_POLISH_MODELS],
        )
    except OllamaError as exc:
        return OllamaServiceStatus(
            available=False,
            base_url=settings.ollama_base_url,
            mock_mode=False,
            message="Ollama 状态检测失败",
            error=str(exc),
            transcription_models=[model_option(model, []) for model in OLLAMA_TRANSCRIPTION_MODELS],
            polish_models=[model_option(model, []) for model in OLLAMA_POLISH_MODELS],
        )

    return OllamaServiceStatus(
        available=True,
        base_url=settings.ollama_base_url,
        mock_mode=False,
        version=str(version_payload.get("version") or ""),
        message="Ollama 服务可用",
        local_models=local_models,
        transcription_models=[model_option(model, local_models) for model in OLLAMA_TRANSCRIPTION_MODELS],
        polish_models=[model_option(model, local_models) for model in OLLAMA_POLISH_MODELS],
    )


def check_model(model_id: str) -> OllamaModelCheck:
    if settings.mock_mode:
        exists = model_id in {"gemma4:12b-it-qat", "gemma4:12b", "gemma3:1b"}
        return OllamaModelCheck(
            model_id=model_id,
            available=exists,
            service_available=True,
            message=f"Mock 模式已检测到 {model_id}" if exists else f"Mock 模式未预置 {model_id}",
        )

    try:
        exists = client().model_exists(model_id)
    except OllamaUnavailableError as exc:
        return OllamaModelCheck(
            model_id=model_id,
            available=False,
            service_available=False,
            message="Ollama 服务不可用，请先启动 Ollama。",
            error=str(exc),
        )
    except OllamaError as exc:
        return OllamaModelCheck(
            model_id=model_id,
            available=False,
            service_available=False,
            message="Ollama 模型检测失败",
            error=str(exc),
        )
    return OllamaModelCheck(
        model_id=model_id,
        available=exists,
        service_available=True,
        message=f"已检测到 {model_id}" if exists else f"未检测到 {model_id}，请选择已安装模型或在应用外手动安装",
    )


def pull_status(model_id: str) -> OllamaPullStatus:
    with tracker_lock:
        tracker = get_tracker(model_id)
        return OllamaPullStatus(
            model_id=model_id,
            state=tracker.state,
            progress=tracker.progress,
            completed_bytes=tracker.completed_bytes,
            total_bytes=tracker.total_bytes,
            progress_label=tracker.progress_label,
            message=tracker.message,
            error=tracker.error,
        )


def request_pull_cancel(model_id: str) -> OllamaPullStatus:
    with tracker_lock:
        tracker = get_tracker(model_id)
        if tracker.state == ModelDownloadState.downloading:
            tracker.cancel_requested = True
            tracker.message = "正在取消 Ollama 模型下载"
        return OllamaPullStatus(
            model_id=model_id,
            state=tracker.state,
            progress=tracker.progress,
            completed_bytes=tracker.completed_bytes,
            total_bytes=tracker.total_bytes,
            progress_label=tracker.progress_label,
            message=tracker.message,
            error=tracker.error,
        )


def pull_model(model_id: str) -> None:
    with tracker_lock:
        tracker = get_tracker(model_id)
        if tracker.state == ModelDownloadState.downloading:
            return
        tracker.state = ModelDownloadState.downloading
        tracker.message = f"正在通过 Ollama 下载 {model_id}"
        tracker.error = None
        tracker.cancel_requested = False
        tracker.progress = 0
        tracker.completed_bytes = None
        tracker.total_bytes = None
        tracker.progress_label = "准备下载"

    def is_canceled() -> bool:
        with tracker_lock:
            return get_tracker(model_id).cancel_requested

    def on_progress(status: str, completed: int | None, total: int | None) -> None:
        progress = 0
        if completed is not None and total:
            progress = max(0, min(99, int(completed * 100 / total)))
        elif "success" in status.lower():
            progress = 100
        else:
            with tracker_lock:
                progress = min(95, max(get_tracker(model_id).progress, 5))
        with tracker_lock:
            tracker = get_tracker(model_id)
            tracker.progress = progress
            tracker.completed_bytes = completed
            tracker.total_bytes = total
            tracker.progress_label = status
            tracker.message = f"{status}：{progress}%"

    try:
        if settings.mock_mode:
            for progress in [10, 35, 65, 90, 100]:
                if is_canceled():
                    raise OllamaPullCanceled("已取消 Ollama 模型下载")
                with tracker_lock:
                    tracker = get_tracker(model_id)
                    tracker.progress = progress
                    tracker.completed_bytes = progress
                    tracker.total_bytes = 100
                    tracker.progress_label = "Mock 下载进度"
                    tracker.message = f"Mock 下载进度：{progress}%"
                time.sleep(0.25)
            with tracker_lock:
                tracker = get_tracker(model_id)
                tracker.state = ModelDownloadState.completed
                tracker.message = f"{model_id} mock 下载完成"
                tracker.error = None
                tracker.cancel_requested = False
                tracker.progress = 100
                tracker.progress_label = "下载完成"
            return

        client().pull_model(model_id, on_progress, is_canceled)
        with tracker_lock:
            tracker = get_tracker(model_id)
            tracker.state = ModelDownloadState.completed
            tracker.message = f"{model_id} 下载完成"
            tracker.error = None
            tracker.cancel_requested = False
            tracker.progress = 100
            tracker.progress_label = "下载完成"
    except OllamaPullCanceled as exc:
        with tracker_lock:
            tracker = get_tracker(model_id)
            tracker.state = ModelDownloadState.canceled
            tracker.message = str(exc)
            tracker.error = None
            tracker.cancel_requested = False
            tracker.progress_label = "已取消"
    except Exception as exc:
        with tracker_lock:
            tracker = get_tracker(model_id)
            tracker.state = ModelDownloadState.failed
            tracker.message = "Ollama 模型下载失败"
            tracker.error = str(exc)
            tracker.cancel_requested = False
            tracker.progress_label = "下载失败"


def model_id_in_list(model_id: str, models: list[str]) -> bool:
    target = normalize(model_id)
    return any(normalize(name) == target for name in models)


def normalize(model_id: str) -> str:
    return model_id if ":" in model_id else f"{model_id}:latest"


def preflight(model_id: str, task: str) -> OllamaPreflightStatus:
    warnings: list[str] = []
    if settings.mock_mode:
        return OllamaPreflightStatus(
            model_id=model_id,
            task=task,
            service_available=True,
            model_exists=model_id in {"gemma4:12b-it-qat", "gemma4:12b", "gemma3:1b"},
            can_generate=True,
            warnings=["Mock 模式：不会调用真实模型"],
            message="Mock 模式 preflight 通过",
        )

    check = check_model(model_id)
    if not check.service_available:
        return OllamaPreflightStatus(
            model_id=model_id,
            task=task,
            service_available=False,
            model_exists=False,
            can_generate=False,
            warnings=warnings,
            message="Ollama 服务不可用，请先启动 Ollama。",
            error=check.error,
        )
    if not check.available:
        return OllamaPreflightStatus(
            model_id=model_id,
            task=task,
            service_available=True,
            model_exists=False,
            can_generate=False,
            warnings=warnings,
            message=f"未检测到 {model_id}，请选择已安装模型或在应用外手动安装",
        )
    if task == "direct_audio":
        warnings.append("当前音频直转能力为实验性；如果 Ollama HTTP API 不支持音频输入，任务会失败。")
    return OllamaPreflightStatus(
        model_id=model_id,
        task=task,
        service_available=True,
        model_exists=True,
        can_generate=True,
        warnings=warnings,
        message="Ollama preflight 通过",
    )
