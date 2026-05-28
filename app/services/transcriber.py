from __future__ import annotations

import multiprocessing as mp
import os
import queue
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from faster_whisper import WhisperModel

from app.config import ROOT_DIR, settings
from app.services.exporters import TranscriptSegment
from app.services.media import OperationCanceled
from app.services.model_manager import clear_runtime_device, current_model_id, resolve_model_path, set_runtime_device


class TranscriptionProcessError(RuntimeError):
    def __init__(self, exitcode: int | None) -> None:
        self.exitcode = exitcode
        super().__init__(f"转写进程异常退出，退出码 {exitcode}")


def configure_runtime() -> None:
    os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
    default_dirs = [ROOT_DIR / "origin-code"]
    env_dirs = [Path(item.strip()) for item in os.getenv("AUDIO_TRANSCRIBE_DLL_DIRS", "").split(os.pathsep) if item.strip()]
    for path in [*default_dirs, *env_dirs]:
        if path.exists() and hasattr(os, "add_dll_directory"):
            os.add_dll_directory(str(path))


def create_model(model_path: Path, device: str, compute_type: str) -> WhisperModel:
    return WhisperModel(str(model_path), device=device, compute_type=compute_type)


def is_cuda_library_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return any(token in text for token in ["cublas", "cudnn", "cuda", "could not load library", "cannot be loaded"])


def cpu_fallback_enabled() -> bool:
    return os.getenv("AUDIO_TRANSCRIBE_CPU_FALLBACK", "1") not in {"0", "false", "False"}


@lru_cache(maxsize=8)
def get_model_bundle(
    model_id: str,
    device: str | None = None,
    compute_type: str | None = None,
) -> tuple[WhisperModel, dict[str, str]]:
    configure_runtime()
    requested_device = device or settings.device
    requested_compute_type = compute_type or settings.compute_type
    model_path = resolve_model_path(model_id)
    if model_path is None:
        clear_runtime_device()
        managed_path = settings.managed_model_path_for(model_id)
        raise FileNotFoundError(
            f"未找到 Whisper 模型目录。请下载模型到 {managed_path}，"
            "或设置 AUDIO_TRANSCRIBE_MODEL_PATH。"
        )

    try:
        model = create_model(model_path, requested_device, requested_compute_type)
        set_runtime_device(requested_device, requested_compute_type)
        return model, {
            "model_id": model_id,
            "path": str(model_path),
            "device": requested_device,
            "compute_type": requested_compute_type,
        }
    except Exception as exc:
        if requested_device == "cuda" and cpu_fallback_enabled() and is_cuda_library_error(exc):
            model = create_model(model_path, "cpu", "int8")
            set_runtime_device("cpu", "int8")
            return model, {
                "model_id": model_id,
                "path": str(model_path),
                "device": "cpu",
                "compute_type": "int8",
            }
        clear_runtime_device()
        raise


def get_model() -> WhisperModel:
    return get_model_bundle(current_model_id())[0]


def _transcribe_worker(
    audio_path: str,
    language: str | None,
    model_id: str,
    device: str,
    compute_type: str,
    result_queue: mp.Queue,
) -> None:
    try:
        result_queue.put({"type": "status", "stage": "loading_model", "model": {"model_id": model_id}})
        model, model_meta = get_model_bundle(model_id, device, compute_type)
        result_queue.put({"type": "status", "stage": "model_loaded", "model": model_meta})
        whisper_language = None if language in {None, "", "auto"} else language
        segments, _info = model.transcribe(
            audio_path,
            beam_size=5,
            language=whisper_language,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )
        result_queue.put({"type": "status", "stage": "transcribing", "model": model_meta})
        transcript = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                transcript.append({"start": segment.start, "end": segment.end, "text": text})
        result_queue.put({"type": "result", "segments": transcript})
    except Exception as exc:
        result_queue.put({"type": "error", "message": str(exc)})


def stop_process(process: mp.Process) -> None:
    if not process.is_alive():
        return
    process.terminate()
    process.join(timeout=5)
    if process.is_alive() and hasattr(process, "kill"):
        process.kill()
        process.join(timeout=2)


def transcribe_audio(
    audio_path: Path,
    language: str | None,
    is_canceled: Callable[[], bool] = lambda: False,
    on_status: Callable[[str, dict[str, str] | None], None] | None = None,
    model_id: str | None = None,
) -> list[TranscriptSegment]:
    model_id = model_id or current_model_id()
    attempts = [(settings.device, settings.compute_type)]
    if settings.device == "cuda" and cpu_fallback_enabled():
        attempts.append(("cpu", "int8"))

    first_error: Exception | None = None
    for index, (device, compute_type) in enumerate(attempts):
        if index > 0 and on_status:
            on_status("fallback_cpu", {"model_id": model_id, "device": device, "compute_type": compute_type})
        try:
            return _transcribe_audio_once(audio_path, language, is_canceled, on_status, model_id, device, compute_type)
        except OperationCanceled:
            raise
        except Exception as exc:
            if first_error is None:
                first_error = exc
            can_retry = index == 0 and len(attempts) > 1
            if can_retry and (isinstance(exc, TranscriptionProcessError) or is_cuda_library_error(exc)):
                continue
            if first_error is not exc and first_error is not None:
                raise RuntimeError(f"{first_error}；CPU 重试也失败：{exc}") from exc
            raise

    raise RuntimeError(str(first_error) if first_error else "转写失败")


def _transcribe_audio_once(
    audio_path: Path,
    language: str | None,
    is_canceled: Callable[[], bool],
    on_status: Callable[[str, dict[str, str] | None], None] | None,
    model_id: str,
    device: str,
    compute_type: str,
) -> list[TranscriptSegment]:
    context = mp.get_context("spawn")
    result_queue: mp.Queue = context.Queue()
    process = context.Process(
        target=_transcribe_worker,
        args=(str(audio_path), language, model_id, device, compute_type, result_queue),
    )
    process.start()

    try:
        while True:
            if is_canceled():
                stop_process(process)
                raise OperationCanceled("任务已停止")
            try:
                message: dict[str, Any] = result_queue.get(timeout=0.3)
            except queue.Empty:
                if not process.is_alive():
                    process.join(timeout=1)
                    if process.exitcode in (0, None):
                        raise RuntimeError("转写进程已退出但没有返回结果")
                    raise TranscriptionProcessError(process.exitcode)
                continue

            message_type = message.get("type")
            if message_type == "status":
                if on_status:
                    on_status(str(message.get("stage")), message.get("model"))
                continue
            if message_type == "result":
                process.join(timeout=2)
                return [TranscriptSegment(**segment) for segment in message.get("segments", [])]
            if message_type == "error":
                process.join(timeout=2)
                raise RuntimeError(message.get("message") or "转写失败")
    finally:
        if is_canceled():
            stop_process(process)
        result_queue.close()
