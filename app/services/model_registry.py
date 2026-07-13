from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Iterable

import httpx

from app.config import settings
from app.schemas import (
    AudioModelTestRequest,
    AudioModelTestResult,
    CustomModelRegistration,
    ModelCapabilities,
    ModelMetadata,
    ModelRegistryStatus,
    UnifiedModel,
)
from app.services.local_model_detection import format_bytes, parse_size


REGISTRY_TIMEOUT_SECONDS = 0.35
REGISTRY_CACHE_SECONDS = 2.0
CUSTOM_MODELS_FILE = settings.data_dir / "custom_models.json"
_registry_cache_lock = Lock()
_registry_cache: tuple[float, ModelRegistryStatus] | None = None


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_model_id(provider: str, path_or_id: str) -> str:
    clean = path_or_id.strip().replace("\\", "/")
    return f"{provider}:{clean}"


def capabilities_for_name(name: str, provider: str) -> ModelCapabilities:
    lower = name.lower()
    is_qwen_audio = any(token in lower for token in ["qwen2-audio", "qwen-audio", "qwen_audio"])
    is_gemma4 = "gemma4" in lower
    audio = any(token in lower for token in ["whisper", "audio", "asr", "speech"]) or is_qwen_audio or is_gemma4
    vision = any(token in lower for token in ["vision", "vl", "llava", "qwen2-vl", "qwen-vl"])
    text = provider in {"ollama", "llama.cpp", "huggingface", "custom"} and (not audio or is_qwen_audio or is_gemma4)
    if provider == "mlx":
        text = is_qwen_audio or is_gemma4 or any(token in lower for token in ["llm", "text", "instruct", "chat"])
    return ModelCapabilities(audio=audio, text=text or provider in {"ollama", "llama.cpp"}, vision=vision or None)


def unified_model(
    *,
    name: str,
    provider: str,
    path_or_id: str,
    capabilities: ModelCapabilities | None = None,
    status: str = "available",
    source: str = "auto_detected",
    detail: str | None = None,
    size: int | None = None,
    modified_at: str | None = None,
    error: str | None = None,
    checked_at: str | None = None,
) -> UnifiedModel:
    checked = checked_at or utc_now_iso()
    return UnifiedModel(
        id=stable_model_id(provider, path_or_id),
        name=name,
        provider=provider,  # type: ignore[arg-type]
        path_or_id=path_or_id,
        capabilities=capabilities or capabilities_for_name(name, provider),
        metadata=ModelMetadata(
            source=source,  # type: ignore[arg-type]
            status=status,  # type: ignore[arg-type]
            last_checked=checked,
            detail=detail,
            size=size,
            size_label=format_bytes(size),
            modified_at=modified_at,
            error=error,
        ),
    )


def discover_ollama(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/tags"
    try:
        response = httpx.get(url, timeout=REGISTRY_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return [], [f"Ollama: {exc}"]

    models: list[UnifiedModel] = []
    for item in payload.get("models") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if not name:
            continue
        models.append(
            unified_model(
                name=name,
                provider="ollama",
                path_or_id=name,
                capabilities=capabilities_for_name(name, "ollama"),
                size=parse_size(item.get("size")),
                modified_at=str(item.get("modified_at") or "") or None,
                checked_at=checked_at,
            )
        )
    return models, []


def scan_roots_from_env(env_name: str) -> list[Path]:
    raw = os.getenv(env_name, "")
    return [Path(item).expanduser() for item in raw.split(os.pathsep) if item.strip()]


def candidate_mlx_roots() -> list[Path]:
    return unique_paths(
        [
            *scan_roots_from_env("AUDIO_TRANSCRIBE_MLX_MODEL_DIRS"),
            settings.model_root,
            Path.home() / ".cache" / "huggingface" / "hub",
        ]
    )


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = str(path.expanduser().resolve(strict=False))
        if key in seen:
            continue
        seen.add(key)
        unique.append(path)
    return unique


def looks_like_model_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    markers = {"config.json", "tokenizer.json", "model.safetensors", "model.bin", "weights.safetensors"}
    try:
        names = {item.name for item in path.iterdir()}
    except OSError:
        return False
    return bool(names & markers or (path / "snapshots").is_dir())


def path_capabilities(path: Path, provider: str) -> ModelCapabilities:
    return capabilities_for_name(path.name.replace("--", "/"), provider)


def discover_mlx(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    models: list[UnifiedModel] = []
    errors: list[str] = []
    for root in candidate_mlx_roots():
        if not root.exists():
            continue
        try:
            candidates = [root, *[item for item in root.glob("*") if item.is_dir()]]
        except OSError as exc:
            errors.append(f"MLX scan {root}: {exc}")
            continue
        for candidate in candidates[:300]:
            if not looks_like_model_dir(candidate):
                continue
            name = candidate.name.replace("models--", "").replace("--", "/")
            caps = path_capabilities(candidate, "mlx")
            if not caps.audio:
                continue
            models.append(
                unified_model(
                    name=name,
                    provider="mlx",
                    path_or_id=str(candidate),
                    capabilities=caps,
                    checked_at=checked_at,
                )
            )
    return models, errors


def hf_cache_root() -> Path:
    return Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface")).expanduser() / "hub"


def discover_huggingface_cache(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    root = hf_cache_root()
    if not root.exists():
        return [], []
    models: list[UnifiedModel] = []
    errors: list[str] = []
    try:
        repos = [item for item in root.glob("models--*") if item.is_dir()]
    except OSError as exc:
        return [], [f"HuggingFace cache: {exc}"]
    for repo in repos[:250]:
        name = repo.name.removeprefix("models--").replace("--", "/")
        snapshots = repo / "snapshots"
        if not snapshots.exists():
            continue
        try:
            latest = max((item for item in snapshots.iterdir() if item.is_dir()), key=lambda item: item.stat().st_mtime)
        except (OSError, ValueError) as exc:
            errors.append(f"HuggingFace cache {repo}: {exc}")
            continue
        caps = capabilities_for_name(name, "huggingface")
        if not caps.audio and not caps.text and not caps.vision:
            continue
        models.append(
            unified_model(
                name=name,
                provider="huggingface",
                path_or_id=str(latest),
                capabilities=caps,
                modified_at=datetime.fromtimestamp(latest.stat().st_mtime, timezone.utc).isoformat(),
                checked_at=checked_at,
            )
        )
    return models, errors


def discover_llamacpp(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    url = os.getenv("AUDIO_TRANSCRIBE_LLAMACPP_MODELS_URL", "http://localhost:8080/v1/models")
    try:
        response = httpx.get(url, timeout=REGISTRY_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        return [], [f"llama.cpp: {exc}"]
    raw_models = payload.get("data") if isinstance(payload, dict) else payload
    models: list[UnifiedModel] = []
    for item in raw_models or []:
        if isinstance(item, str):
            model_id = item
        elif isinstance(item, dict):
            model_id = str(item.get("id") or item.get("name") or item.get("model") or "").strip()
        else:
            model_id = ""
        if not model_id:
            continue
        models.append(
            unified_model(
                name=model_id,
                provider="llama.cpp",
                path_or_id=model_id,
                capabilities=ModelCapabilities(audio=False, text=True),
                checked_at=checked_at,
            )
        )
    return models, []


def read_custom_models() -> list[CustomModelRegistration]:
    if not CUSTOM_MODELS_FILE.exists():
        return []
    try:
        payload = json.loads(CUSTOM_MODELS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    models: list[CustomModelRegistration] = []
    for item in payload:
        try:
            models.append(CustomModelRegistration(**item))
        except Exception:
            continue
    return models


def custom_path_or_id_is_path_like(path_or_id: str) -> bool:
    value = path_or_id.strip()
    if not value:
        return False
    return value.startswith(("/", "~", ".")) or "\\" in value


def custom_path_or_id_exists(path_or_id: str) -> bool:
    value = path_or_id.strip()
    if not value:
        return False
    if custom_path_or_id_is_path_like(value):
        return Path(value).expanduser().exists()
    return True


def write_custom_models(models: list[CustomModelRegistration]) -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    CUSTOM_MODELS_FILE.write_text(
        json.dumps([model.model_dump() for model in models], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    invalidate_model_registry_cache()


def discover_custom(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    models = []
    for item in read_custom_models():
        path_or_id = item.path_or_id.strip()
        exists = custom_path_or_id_exists(path_or_id)
        models.append(
            unified_model(
                name=item.name or Path(path_or_id).name or path_or_id,
                provider=item.provider,
                path_or_id=path_or_id,
                capabilities=item.capabilities,
                status="available" if exists else "missing",
                source="user_added",
                detail="用户注册模型",
                checked_at=checked_at,
            )
        )
    return models, []


def probe_custom_model(request: CustomModelRegistration) -> UnifiedModel:
    path_or_id = request.path_or_id.strip()
    checked = utc_now_iso()
    exists = custom_path_or_id_exists(path_or_id)
    return unified_model(
        name=request.name or Path(path_or_id).name or path_or_id,
        provider=request.provider,
        path_or_id=path_or_id,
        capabilities=request.capabilities,
        status="available" if exists else "missing",
        source="user_added",
        detail="输入路径检测",
        checked_at=checked,
    )


def register_custom_model(request: CustomModelRegistration) -> UnifiedModel:
    models = read_custom_models()
    next_model = CustomModelRegistration(
        name=request.name,
        provider=request.provider,
        path_or_id=request.path_or_id.strip(),
        capabilities=request.capabilities,
    )
    models = [item for item in models if not (item.provider == next_model.provider and item.path_or_id == next_model.path_or_id)]
    models.append(next_model)
    write_custom_models(models)
    checked = utc_now_iso()
    return unified_model(
        name=next_model.name or Path(next_model.path_or_id).name or next_model.path_or_id,
        provider=next_model.provider,
        path_or_id=next_model.path_or_id,
        capabilities=next_model.capabilities,
        status="available" if custom_path_or_id_exists(next_model.path_or_id) else "missing",
        source="user_added",
        detail="用户注册模型",
        checked_at=checked,
    )


def delete_custom_model(provider: str, path_or_id: str) -> bool:
    target_provider = provider.strip()
    target_path = path_or_id.strip()
    models = read_custom_models()
    remaining = [
        item for item in models if not (item.provider == target_provider and item.path_or_id == target_path)
    ]
    if len(remaining) == len(models):
        return False
    write_custom_models(remaining)
    return True


def invalidate_model_registry_cache() -> None:
    global _registry_cache
    with _registry_cache_lock:
        _registry_cache = None


def _run_registry_detectors(checked_at: str) -> tuple[list[UnifiedModel], list[str]]:
    detectors = (discover_ollama, discover_mlx, discover_huggingface_cache, discover_llamacpp, discover_custom)
    model_groups: list[UnifiedModel] = []
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=len(detectors)) as pool:
        futures = {pool.submit(detector, checked_at): getattr(detector, "__name__", repr(detector)) for detector in detectors}
        for future in as_completed(futures):
            detector_name = futures[future]
            try:
                models, detector_errors = future.result()
            except Exception as exc:
                errors.append(f"{detector_name}: {exc}")
                continue
            model_groups.extend(models)
            errors.extend(detector_errors)
    return model_groups, errors


def model_registry(*, force_refresh: bool = False) -> ModelRegistryStatus:
    global _registry_cache
    now = time.monotonic()
    if not force_refresh:
        with _registry_cache_lock:
            if _registry_cache is not None:
                cached_at, cached_status = _registry_cache
                if now - cached_at < REGISTRY_CACHE_SECONDS:
                    return cached_status

    checked_at = utc_now_iso()
    model_groups, errors = _run_registry_detectors(checked_at)
    deduped: dict[str, UnifiedModel] = {}
    for model in model_groups:
        deduped[model.id] = model
    status = ModelRegistryStatus(checked_at=checked_at, models=list(deduped.values()), errors=errors)
    with _registry_cache_lock:
        _registry_cache = (time.monotonic(), status)
    return status


def test_audio_model(request: AudioModelTestRequest) -> AudioModelTestResult:
    start = time.perf_counter()
    registry = model_registry(force_refresh=True)
    model = next((item for item in registry.models if item.id == request.model_id), None)
    latency_ms = int((time.perf_counter() - start) * 1000)
    if not model:
        return AudioModelTestResult(
            success=False,
            latency_ms=latency_ms,
            message="模型不在当前检测结果中。",
            error="MODEL_NOT_DETECTED",
        )
    if not model.capabilities.audio:
        return AudioModelTestResult(
            success=False,
            latency_ms=latency_ms,
            message="该模型未声明 Audio Input 能力。",
            error="AUDIO_CAPABILITY_MISSING",
        )
    if model.metadata.status != "available":
        return AudioModelTestResult(
            success=False,
            latency_ms=latency_ms,
            message="模型当前不可用。",
            error=model.metadata.error or model.metadata.status,
        )
    return AudioModelTestResult(
        success=True,
        latency_ms=latency_ms,
        message="快速测试通过：模型已检测到且声明支持 Audio Input。实际推理会在任务提交后执行。",
    )
