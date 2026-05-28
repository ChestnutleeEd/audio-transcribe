from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings


SUPPORTED_UPLOAD_SUFFIXES = {
    ".mp3",
    ".m4a",
    ".wav",
    ".flac",
    ".aac",
    ".ogg",
    ".mp4",
    ".mov",
    ".mkv",
    ".webm",
    ".avi",
}


def safe_stem(name: str) -> str:
    keep = []
    for char in Path(name).stem:
        keep.append(char if char.isalnum() or char in ("-", "_") else "_")
    return "".join(keep).strip("_") or "transcript"


def ensure_runtime_dirs() -> None:
    settings.jobs_dir.mkdir(parents=True, exist_ok=True)
    settings.uploads_dir.mkdir(parents=True, exist_ok=True)


def ffmpeg_executable() -> str:
    configured = Path(settings.ffmpeg_path)
    if configured.exists():
        return str(configured)
    found = shutil.which("ffmpeg")
    if found:
        return found
    return settings.ffmpeg_path


def normalize_audio(input_path: Path, output_path: Path, start_time: str | None, end_time: str | None) -> Path:
    command = [ffmpeg_executable(), "-i", str(input_path)]
    if start_time:
        command.extend(["-ss", start_time])
    if end_time:
        command.extend(["-to", end_time])
    command.extend(["-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(output_path), "-y"])

    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "FFmpeg 音频预处理失败")
    return output_path


def download_audio(url: str, output_dir: Path) -> Path:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("仅支持 http/https 视频链接")

    output_template = str(output_dir / "%(title).120s.%(ext)s")
    command = [
        "yt-dlp",
        "--no-playlist",
        "-x",
        "--audio-format",
        "m4a",
        "-o",
        output_template,
        url,
    ]
    result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="ignore")
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "视频音频下载失败")

    candidates = sorted(output_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_UPLOAD_SUFFIXES:
            return candidate
    raise RuntimeError("下载完成但未找到可处理的音频文件")
