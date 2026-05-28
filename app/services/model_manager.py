from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from huggingface_hub import snapshot_download

from app.config import SUPPORTED_MODELS, settings
from app.schemas import ModelDownloadState, ModelOption, ModelStatus


REQUIRED_MODEL_FILES = [
    "config.json",
    "model.bin",
    "tokenizer.json",
    "vocabulary.json",
]


@dataclass
class DownloadTracker:
    state: ModelDownloadState = ModelDownloadState.idle
    message: str = "模型尚未检测"
    error: str | None = None


selected_model_id = settings.model_definition().id
trackers: dict[str, DownloadTracker] = {}
tracker_lock = Lock()
active_device: str | None = None
active_compute_type: str | None = None


def get_tracker(model_id: str) -> DownloadTracker:
    if model_id not in trackers:
        trackers[model_id] = DownloadTracker()
    return trackers[model_id]


def current_model_id() -> str:
    with tracker_lock:
        return selected_model_id


def select_model(model_id: str) -> str:
    model = settings.model_definition(model_id)
    with tracker_lock:
        global selected_model_id, active_device, active_compute_type
        selected_model_id = model.id
        active_device = None
        active_compute_type = None
    return model.id


def set_runtime_device(device: str, compute_type: str) -> None:
    with tracker_lock:
        global active_device, active_compute_type
        active_device = device
        active_compute_type = compute_type


def clear_runtime_device() -> None:
    with tracker_lock:
        global active_device, active_compute_type
        active_device = None
        active_compute_type = None


def is_valid_model_dir(path: Path) -> bool:
    return path.exists() and all((path / file_name).exists() for file_name in REQUIRED_MODEL_FILES)


def resolve_model_path(model_id: str | None = None) -> Path | None:
    for candidate in settings.candidate_model_paths(model_id or current_model_id()):
        if is_valid_model_dir(candidate):
            return candidate
    return None


def model_options() -> list[ModelOption]:
    return [
        ModelOption(
            id=model.id,
            label=model.label,
            repo_id=settings.model_definition(model.id).repo_id,
            managed_path=str(settings.managed_model_path_for(model.id)),
            available=resolve_model_path(model.id) is not None,
        )
        for model in SUPPORTED_MODELS
    ]


def model_status() -> ModelStatus:
    model_id = current_model_id()
    model = settings.model_definition(model_id)
    active_path = resolve_model_path(model.id)
    with tracker_lock:
        tracker = get_tracker(model.id)
        state = tracker.state
        message = tracker.message
        error = tracker.error
        runtime_device = active_device
        runtime_compute_type = active_compute_type

    if active_path:
        state = ModelDownloadState.completed
        message = f"已检测到可用 {model.id} 模型"
        error = None
    elif state == ModelDownloadState.idle:
        message = f"未检测到模型，请确认后下载 {model.id}"

    return ModelStatus(
        available=active_path is not None,
        selected_model=model.id,
        models=model_options(),
        active_path=str(active_path) if active_path else None,
        managed_path=str(settings.managed_model_path_for(model.id)),
        repo_id=model.repo_id,
        required_files=REQUIRED_MODEL_FILES,
        configured_device=settings.device,
        active_device=runtime_device,
        active_compute_type=runtime_compute_type,
        download_state=state,
        message=message,
        error=error,
    )


def download_model(model_id: str | None = None) -> None:
    model = settings.model_definition(model_id or current_model_id())
    managed_path = settings.managed_model_path_for(model.id)
    with tracker_lock:
        tracker = get_tracker(model.id)
        if tracker.state == ModelDownloadState.downloading:
            return
        tracker.state = ModelDownloadState.downloading
        tracker.message = f"正在下载 {model.id} 模型，文件较大，请保持网络连接"
        tracker.error = None

    try:
        managed_path.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=model.repo_id,
            local_dir=str(managed_path),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        if not is_valid_model_dir(managed_path):
            missing = [name for name in REQUIRED_MODEL_FILES if not (managed_path / name).exists()]
            raise RuntimeError(f"模型下载后仍缺少文件: {', '.join(missing)}")

        with tracker_lock:
            tracker = get_tracker(model.id)
            tracker.state = ModelDownloadState.completed
            tracker.message = "模型下载完成"
            tracker.error = None
    except Exception as exc:
        with tracker_lock:
            tracker = get_tracker(model.id)
            tracker.state = ModelDownloadState.failed
            tracker.message = "模型下载失败"
            tracker.error = str(exc)
