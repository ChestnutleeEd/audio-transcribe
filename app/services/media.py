from __future__ import annotations

import shutil
import subprocess
import sys
import time
import os
import socket
from pathlib import Path
from typing import Callable
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


class OperationCanceled(RuntimeError):
    pass


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


def ffmpeg_location() -> str | None:
    configured = Path(settings.ffmpeg_path)
    if configured.exists():
        return str(configured.parent if configured.is_file() else configured)
    found = shutil.which("ffmpeg")
    if found:
        return str(Path(found).parent)
    return None


def run_command(command: list[str], is_canceled: Callable[[], bool]) -> subprocess.CompletedProcess[str]:
    return run_command_with_env(command, is_canceled)


def run_command_with_env(
    command: list[str],
    is_canceled: Callable[[], bool],
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="ignore",
        env=env,
    )
    while process.poll() is None:
        if is_canceled():
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            raise OperationCanceled("任务已停止")
        time.sleep(0.3)
    stdout, stderr = process.communicate()
    return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)


def yt_dlp_command() -> list[str]:
    local_exe = Path(sys.executable).with_name("yt-dlp.exe")
    if local_exe.exists():
        return [str(local_exe)]
    found = shutil.which("yt-dlp")
    if found:
        return [found]
    return [sys.executable, "-m", "yt_dlp"]


def node_runtime_path() -> str | None:
    bundled = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies" / "node" / "bin" / "node.exe"
    if bundled.exists():
        return str(bundled)
    found = shutil.which("node")
    return found


def env_proxy() -> str | None:
    for key in ["AUDIO_TRANSCRIBE_PROXY", "HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy", "ALL_PROXY", "all_proxy"]:
        value = os.getenv(key)
        if value:
            return value
    return None


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.4):
            return True
    except OSError:
        return False


def detected_proxy() -> str | None:
    configured = env_proxy()
    if configured:
        return configured
    for port in [7892, 7890]:
        if port_open(port):
            return f"http://127.0.0.1:{port}"
    return None


def proxy_env(proxy: str | None) -> dict[str, str] | None:
    if not proxy:
        return None
    env = os.environ.copy()
    for key in ["HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy"]:
        env[key] = proxy
    return env


def normalize_audio(
    input_path: Path,
    output_path: Path,
    start_time: str | None,
    end_time: str | None,
    is_canceled: Callable[[], bool] = lambda: False,
) -> Path:
    command = [ffmpeg_executable(), "-i", str(input_path)]
    if start_time:
        command.extend(["-ss", start_time])
    if end_time:
        command.extend(["-to", end_time])
    command.extend(["-vn", "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1", str(output_path), "-y"])

    result = run_command(command, is_canceled)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "FFmpeg 音频预处理失败，请检查文件格式或 FFmpeg 路径")
    return output_path


def download_audio(url: str, output_dir: Path, is_canceled: Callable[[], bool] = lambda: False) -> Path:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError("仅支持 http/https 视频链接")

    output_template = str(output_dir / "%(title).120s.%(ext)s")
    command = [
        *yt_dlp_command(),
        "--no-playlist",
        "--remote-components",
        "ejs:github",
        "-x",
        "--audio-format",
        "m4a",
        "-o",
        output_template,
    ]
    location = ffmpeg_location()
    if location:
        command.extend(["--ffmpeg-location", location])
    node_path = node_runtime_path()
    if node_path:
        command.extend(["--js-runtimes", f"node:{node_path}"])
    proxy = detected_proxy()
    if proxy:
        command.extend(["--proxy", proxy])
    command.append(url)
    result = run_command_with_env(command, is_canceled, proxy_env(proxy))
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "视频音频下载失败，请检查链接、网络或 yt-dlp 支持情况")

    candidates = sorted(output_dir.glob("*"), key=lambda path: path.stat().st_mtime, reverse=True)
    for candidate in candidates:
        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_UPLOAD_SUFFIXES:
            return candidate
    raise RuntimeError("下载完成但未找到可处理的音频文件")
