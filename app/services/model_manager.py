from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from threading import Lock

from huggingface_hub import snapshot_download

from app.config import settings
from app.schemas import ModelDownloadState, ModelStatus


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


tracker = DownloadTracker()
tracker_lock = Lock()


def is_valid_model_dir(path: Path) -> bool:
    return path.exists() and all((path / file_name).exists() for file_name in REQUIRED_MODEL_FILES)


def resolve_model_path() -> Path | None:
    for candidate in settings.candidate_model_paths():
        if is_valid_model_dir(candidate):
            return candidate
    return None


def model_status() -> ModelStatus:
    active_path = resolve_model_path()
    with tracker_lock:
        state = tracker.state
        message = tracker.message
        error = tracker.error

    if active_path:
        state = ModelDownloadState.completed
        message = "已检测到可用 large-v3 模型"
        error = None
    elif state == ModelDownloadState.idle:
        message = "未检测到模型，请确认后下载 large-v3"

    return ModelStatus(
        available=active_path is not None,
        active_path=str(active_path) if active_path else None,
        managed_path=str(settings.managed_model_path),
        repo_id=settings.model_repo_id,
        required_files=REQUIRED_MODEL_FILES,
        download_state=state,
        message=message,
        error=error,
    )


def download_model() -> None:
    with tracker_lock:
        if tracker.state == ModelDownloadState.downloading:
            return
        tracker.state = ModelDownloadState.downloading
        tracker.message = "正在下载 large-v3 模型，文件较大，请保持网络连接"
        tracker.error = None

    try:
        settings.managed_model_path.mkdir(parents=True, exist_ok=True)
        snapshot_download(
            repo_id=settings.model_repo_id,
            local_dir=str(settings.managed_model_path),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        if not is_valid_model_dir(settings.managed_model_path):
            missing = [name for name in REQUIRED_MODEL_FILES if not (settings.managed_model_path / name).exists()]
            raise RuntimeError(f"模型下载后仍缺少文件: {', '.join(missing)}")

        with tracker_lock:
            tracker.state = ModelDownloadState.completed
            tracker.message = "模型下载完成"
            tracker.error = None
    except Exception as exc:
        with tracker_lock:
            tracker.state = ModelDownloadState.failed
            tracker.message = "模型下载失败"
            tracker.error = str(exc)
