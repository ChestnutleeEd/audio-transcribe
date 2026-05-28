from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    app_name: str = "Audio Transcribe"
    model_path: Path = Path(
        os.getenv(
            "AUDIO_TRANSCRIBE_MODEL_PATH",
            ROOT_DIR / "origin-code" / "large-v3-local",
        )
    )
    device: str = os.getenv("AUDIO_TRANSCRIBE_DEVICE", "cuda")
    compute_type: str = os.getenv("AUDIO_TRANSCRIBE_COMPUTE_TYPE", "int8_float16")
    ffmpeg_path: str = os.getenv("AUDIO_TRANSCRIBE_FFMPEG", str(ROOT_DIR / "origin-code" / "ffmpeg.exe"))
    data_dir: Path = Path(os.getenv("AUDIO_TRANSCRIBE_DATA_DIR", ROOT_DIR / "data"))

    @property
    def jobs_dir(self) -> Path:
        return self.data_dir / "jobs"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"


settings = Settings()
