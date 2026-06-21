from __future__ import annotations

import json
from pathlib import Path

from app.config import settings


BINDINGS_FILE = settings.data_dir / "model_bindings.json"


def read_model_bindings() -> dict[str, object]:
    if not BINDINGS_FILE.exists():
        return {}
    try:
        payload = json.loads(BINDINGS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def write_model_bindings(payload: dict[str, object]) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    BINDINGS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def whisper_bindings() -> dict[str, str]:
    payload = read_model_bindings()
    raw = payload.get("whisper_model_paths")
    if not isinstance(raw, dict):
        return {}
    return {str(key): str(value) for key, value in raw.items() if str(value).strip()}


def whisper_model_path(model_id: str) -> Path | None:
    value = whisper_bindings().get(model_id, "").strip()
    return Path(value).expanduser() if value else None


def bind_whisper_model_path(model_id: str, path: Path) -> None:
    payload = read_model_bindings()
    bindings = whisper_bindings()
    bindings[model_id] = str(path.expanduser())
    payload["whisper_model_paths"] = bindings
    write_model_bindings(payload)


def unbind_whisper_model_path(model_id: str) -> None:
    payload = read_model_bindings()
    bindings = whisper_bindings()
    bindings.pop(model_id, None)
    payload["whisper_model_paths"] = bindings
    write_model_bindings(payload)
