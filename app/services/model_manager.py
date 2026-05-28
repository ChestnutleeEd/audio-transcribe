from __future__ import annotations

import multiprocessing as mp
import queue
import threading
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from typing import Any

from huggingface_hub import snapshot_download

from app.config import SUPPORTED_MODELS, settings
from app.schemas import ModelDownloadState, ModelOption, ModelStatus


REQUIRED_MODEL_FILES = [
    "config.json",
    "model.bin",
    "tokenizer.json",
]

VOCABULARY_FILES = ["vocabulary.json", "vocabulary.txt"]


@dataclass
class DownloadTracker:
    state: ModelDownloadState = ModelDownloadState.idle
    message: str = "模型尚未检测"
    error: str | None = None
    cancel_requested: bool = False
    progress: int = 0
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    progress_label: str | None = None


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


def required_model_files() -> list[str]:
    return [*REQUIRED_MODEL_FILES, "vocabulary.json 或 vocabulary.txt"]


def is_valid_model_dir(path: Path) -> bool:
    has_required = path.exists() and all((path / file_name).exists() for file_name in REQUIRED_MODEL_FILES)
    has_vocabulary = any((path / file_name).exists() for file_name in VOCABULARY_FILES)
    return has_required and has_vocabulary


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
        progress = tracker.progress
        downloaded_bytes = tracker.downloaded_bytes
        total_bytes = tracker.total_bytes
        progress_label = tracker.progress_label
        runtime_device = active_device
        runtime_compute_type = active_compute_type

    if active_path:
        state = ModelDownloadState.completed
        message = f"已检测到可用 {model.id} 模型"
        error = None
        progress = 100
        progress_label = "模型已就绪"
    elif state == ModelDownloadState.idle:
        message = f"未检测到模型，请确认后下载 {model.id}"
        progress = 0
        progress_label = None

    return ModelStatus(
        available=active_path is not None,
        selected_model=model.id,
        models=model_options(),
        active_path=str(active_path) if active_path else None,
        managed_path=str(settings.managed_model_path_for(model.id)),
        repo_id=model.repo_id,
        required_files=required_model_files(),
        configured_device=settings.device,
        active_device=runtime_device,
        active_compute_type=runtime_compute_type,
        download_state=state,
        download_progress=progress,
        downloaded_bytes=downloaded_bytes,
        total_bytes=total_bytes,
        download_progress_label=progress_label,
        message=message,
        error=error,
    )


def cleanup_model_download_dir(path: Path) -> None:
    if not path.exists() or not path.is_dir():
        return
    files = [item for item in path.rglob("*") if item.is_file() or item.is_symlink()]
    for item in files:
        try:
            item.unlink()
        except OSError:
            pass
    directories = sorted([item for item in path.rglob("*") if item.is_dir()], key=lambda item: len(item.parts), reverse=True)
    for item in directories:
        try:
            item.rmdir()
        except OSError:
            pass
    try:
        path.rmdir()
    except OSError:
        pass


def _snapshot_download_worker(repo_id: str, managed_path: str, result_queue: mp.Queue) -> None:
    from tqdm.auto import tqdm

    bars: dict[int, dict[str, Any]] = {}
    bars_lock = threading.Lock()

    def publish_progress() -> None:
        with bars_lock:
            byte_bars = [bar for bar in bars.values() if bar.get("unit") == "B" and bar.get("total")]
            active_bars = byte_bars or [bar for bar in bars.values() if bar.get("total")]
            if not active_bars:
                return
            downloaded = sum(int(bar.get("n") or 0) for bar in active_bars)
            total = sum(int(bar.get("total") or 0) for bar in active_bars)
            if total <= 0:
                return
            progress = max(0, min(99, int(downloaded * 100 / total)))
            label = "下载文件" if byte_bars else "获取文件列表"
            result_queue.put(
                {
                    "type": "progress",
                    "progress": progress,
                    "downloaded_bytes": downloaded if byte_bars else None,
                    "total_bytes": total if byte_bars else None,
                    "label": label,
                }
            )

    class QueueTqdm(tqdm):
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            with bars_lock:
                bars[id(self)] = {"n": int(self.n or 0), "total": self.total, "unit": getattr(self, "unit", None)}
            publish_progress()

        def update(self, n: int = 1) -> bool | None:
            result = super().update(n)
            with bars_lock:
                if id(self) in bars:
                    bars[id(self)] = {"n": int(self.n or 0), "total": self.total, "unit": getattr(self, "unit", None)}
            publish_progress()
            return result

        def close(self) -> None:
            with bars_lock:
                if id(self) in bars:
                    bars[id(self)] = {"n": int(self.n or 0), "total": self.total, "unit": getattr(self, "unit", None)}
            publish_progress()
            super().close()

    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=managed_path,
            local_dir_use_symlinks=False,
            resume_download=True,
            tqdm_class=QueueTqdm,
        )
        result_queue.put({"type": "completed"})
    except Exception as exc:
        result_queue.put({"type": "error", "message": str(exc)})


def friendly_download_error(error: str) -> str:
    text = error.lower()
    if "connecterror" in text or "ssl" in text or "unexpected_eof" in text or "connection" in text:
        return (
            "模型下载失败：连接 Hugging Face 时网络或 SSL 连接中断。"
            "请检查代理/网络后重试；已保留取消按钮用于中止并清理本次下载。"
        )
    return error


def request_model_download_cancel(model_id: str | None = None) -> None:
    model = settings.model_definition(model_id or current_model_id())
    with tracker_lock:
        tracker = get_tracker(model.id)
        if tracker.state == ModelDownloadState.downloading:
            tracker.cancel_requested = True
            tracker.message = "正在取消模型下载并清理已下载内容"


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
        tracker.cancel_requested = False
        tracker.progress = 0
        tracker.downloaded_bytes = None
        tracker.total_bytes = None
        tracker.progress_label = "准备下载"

    result_queue: mp.Queue = mp.get_context("spawn").Queue()
    process = mp.get_context("spawn").Process(
        target=_snapshot_download_worker,
        args=(model.repo_id, str(managed_path), result_queue),
    )
    try:
        managed_path.mkdir(parents=True, exist_ok=True)
        process.start()
        result: dict[str, Any] | None = None
        while process.is_alive():
            with tracker_lock:
                should_cancel = get_tracker(model.id).cancel_requested
            if should_cancel:
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=2)
                cleanup_model_download_dir(managed_path)
                with tracker_lock:
                    tracker = get_tracker(model.id)
                    tracker.state = ModelDownloadState.canceled
                    tracker.message = "已取消模型下载，并清理本次下载内容"
                    tracker.error = None
                    tracker.cancel_requested = False
                return
            try:
                result = result_queue.get(timeout=0.4)
                if result.get("type") == "progress":
                    with tracker_lock:
                        tracker = get_tracker(model.id)
                        tracker.progress = int(result.get("progress") or 0)
                        tracker.downloaded_bytes = result.get("downloaded_bytes")
                        tracker.total_bytes = result.get("total_bytes")
                        tracker.progress_label = str(result.get("label") or "下载中")
                        tracker.message = f"{tracker.progress_label}：{tracker.progress}%"
                    result = None
                    continue
                break
            except queue.Empty:
                continue

        process.join(timeout=2)
        while result is None or result.get("type") == "progress":
            try:
                next_result = result_queue.get_nowait()
            except queue.Empty:
                if result is None:
                    result = {"type": "error", "message": f"模型下载进程异常退出，退出码 {process.exitcode}"}
                else:
                    break
            else:
                if next_result.get("type") == "progress":
                    with tracker_lock:
                        tracker = get_tracker(model.id)
                        tracker.progress = int(next_result.get("progress") or 0)
                        tracker.downloaded_bytes = next_result.get("downloaded_bytes")
                        tracker.total_bytes = next_result.get("total_bytes")
                        tracker.progress_label = str(next_result.get("label") or "下载中")
                        tracker.message = f"{tracker.progress_label}：{tracker.progress}%"
                    result = next_result
                    continue
                result = next_result
        if result.get("type") == "error":
            raise RuntimeError(str(result.get("message") or "模型下载失败"))

        if not is_valid_model_dir(managed_path):
            missing = [name for name in REQUIRED_MODEL_FILES if not (managed_path / name).exists()]
            if not any((managed_path / name).exists() for name in VOCABULARY_FILES):
                missing.append("vocabulary.json 或 vocabulary.txt")
            raise RuntimeError(f"模型下载后仍缺少文件: {', '.join(missing)}")

        with tracker_lock:
            tracker = get_tracker(model.id)
            tracker.state = ModelDownloadState.completed
            tracker.message = "模型下载完成"
            tracker.error = None
            tracker.cancel_requested = False
            tracker.progress = 100
            tracker.progress_label = "下载完成"
    except Exception as exc:
        if process.is_alive():
            process.terminate()
            process.join(timeout=5)
        with tracker_lock:
            tracker = get_tracker(model.id)
            tracker.state = ModelDownloadState.failed
            tracker.message = "模型下载失败"
            tracker.error = friendly_download_error(str(exc))
            tracker.cancel_requested = False
            tracker.progress_label = "下载失败"
    finally:
        result_queue.close()
