from __future__ import annotations

import json
import subprocess
import wave
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from app.services.media import OperationCanceled, ffmpeg_executable, terminate_process


@dataclass(frozen=True)
class AudioChunk:
    chunk_id: int
    start: float
    end: float
    audio_path: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _run_ffmpeg(command: list[str], is_canceled: Callable[[], bool]) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    while process.poll() is None:
        if is_canceled():
            terminate_process(process)
            raise OperationCanceled("任务已停止")
    stdout, stderr = process.communicate()
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def _probe_duration_with_ffprobe(audio_path: Path) -> float | None:
    ffmpeg_path = Path(ffmpeg_executable())
    candidates = []
    if ffmpeg_path.name.lower().startswith("ffmpeg"):
        candidates.append(ffmpeg_path.with_name("ffprobe" + ffmpeg_path.suffix))
    candidates.append(Path("ffprobe"))

    for candidate in candidates:
        command = [
            str(candidate),
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(audio_path),
        ]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=20)
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode != 0:
            continue
        try:
            payload = json.loads(result.stdout or "{}")
            duration = float(payload.get("format", {}).get("duration") or 0)
        except (TypeError, ValueError, json.JSONDecodeError):
            continue
        if duration > 0:
            return duration
    return None


def audio_duration_seconds(audio_path: Path) -> float:
    duration = _probe_duration_with_ffprobe(audio_path)
    if duration:
        return duration
    if audio_path.suffix.lower() == ".wav":
        with wave.open(str(audio_path), "rb") as handle:
            frames = handle.getnframes()
            rate = handle.getframerate()
            return frames / float(rate)
    raise RuntimeError("无法读取音频时长，请确认 FFprobe 可用或输入为 WAV 文件。")


def normalize_to_16k_mono(
    input_path: Path,
    output_path: Path,
    is_canceled: Callable[[], bool] = lambda: False,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        ffmpeg_executable(),
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_path),
    ]
    result = _run_ffmpeg(command, is_canceled)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Qwen2-Audio 音频预处理失败，请检查文件格式或 FFmpeg 路径。")
    return output_path


def chunk_audio(
    audio_path: Path,
    chunk_dir: Path,
    chunk_seconds: float = 20.0,
    overlap_seconds: float = 1.0,
    is_canceled: Callable[[], bool] = lambda: False,
) -> list[AudioChunk]:
    if chunk_seconds < 15 or chunk_seconds > 30:
        raise ValueError("Qwen2-Audio chunk_seconds 必须在 15 到 30 秒之间。")
    if overlap_seconds < 0 or overlap_seconds > 2:
        raise ValueError("Qwen2-Audio overlap_seconds 必须在 0 到 2 秒之间。")
    if overlap_seconds >= chunk_seconds:
        raise ValueError("Qwen2-Audio overlap_seconds 必须小于 chunk_seconds。")

    duration = audio_duration_seconds(audio_path)
    chunk_dir.mkdir(parents=True, exist_ok=True)
    chunks: list[AudioChunk] = []
    start = 0.0
    chunk_id = 1
    step = chunk_seconds - overlap_seconds
    while start < duration:
        if is_canceled():
            raise OperationCanceled("任务已停止")
        end = min(duration, start + chunk_seconds)
        chunk_path = chunk_dir / f"chunk_{chunk_id:04d}.wav"
        command = [
            ffmpeg_executable(),
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(audio_path),
            "-t",
            f"{end - start:.3f}",
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(chunk_path),
        ]
        result = _run_ffmpeg(command, is_canceled)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or f"Qwen2-Audio 第 {chunk_id} 段切分失败。")
        chunks.append(AudioChunk(chunk_id=chunk_id, start=round(start, 3), end=round(end, 3), audio_path=str(chunk_path)))
        if end >= duration:
            break
        start += step
        chunk_id += 1
    return chunks


def prepare_audio_chunks(
    input_path: Path,
    work_dir: Path,
    chunk_seconds: float = 20.0,
    overlap_seconds: float = 1.0,
    namespace: str = "qwen_audio",
    is_canceled: Callable[[], bool] = lambda: False,
) -> list[dict[str, object]]:
    normalized_path = work_dir / namespace / "input_16k_mono.wav"
    chunk_dir = work_dir / namespace / "chunks"
    normalize_to_16k_mono(input_path, normalized_path, is_canceled)
    return [
        chunk.as_dict()
        for chunk in chunk_audio(
            normalized_path,
            chunk_dir,
            chunk_seconds=chunk_seconds,
            overlap_seconds=overlap_seconds,
            is_canceled=is_canceled,
        )
    ]
