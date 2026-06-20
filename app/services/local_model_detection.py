from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from app.config import settings
from app.schemas import LocalDetectedModel, LocalModelDetectionStatus, LocalModelProviderStatus


DETECTION_TIMEOUT_SECONDS = 1.5


@dataclass(frozen=True)
class LocalModelProvider:
    id: str
    name: str
    type: str
    url: str
    detect: Callable[["LocalModelProvider"], LocalModelProviderStatus]


def format_bytes(size: int | None) -> str | None:
    if size is None:
        return None
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(size)
    unit_index = 0
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    return f"{value:.1f} {units[unit_index]}" if unit_index else f"{int(value)} B"


def parse_size(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def provider_error_status(provider: LocalModelProvider, message: str, error: str) -> LocalModelProviderStatus:
    return LocalModelProviderStatus(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        url=provider.url,
        online=False,
        can_polish=False,
        message=message,
        error=error,
        models=[],
    )


def detect_ollama_models(provider: LocalModelProvider) -> LocalModelProviderStatus:
    try:
        response = httpx.get(provider.url, timeout=DETECTION_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except httpx.RequestError as exc:
        return provider_error_status(provider, "Ollama 未在线或端口不可访问。", str(exc))
    except httpx.HTTPStatusError as exc:
        return provider_error_status(provider, f"Ollama 返回 HTTP {exc.response.status_code}。", str(exc))
    except ValueError as exc:
        return provider_error_status(provider, "Ollama 返回内容不是有效 JSON。", str(exc))

    models = []
    for item in payload.get("models") or []:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name") or item.get("model") or "").strip()
        if not name:
            continue
        size = parse_size(item.get("size"))
        models.append(
            LocalDetectedModel(
                provider_id=provider.id,
                provider=provider.name,
                provider_type=provider.type,
                name=name,
                id=name,
                size=size,
                size_label=format_bytes(size),
                modified_at=str(item.get("modified_at") or "") or None,
                can_polish=True,
                recommendation="可用于当前 Ollama polish 流程。",
            )
        )
    return LocalModelProviderStatus(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        url=provider.url,
        online=True,
        can_polish=True,
        message=f"检测到 {len(models)} 个 Ollama 本地模型。" if models else "Ollama 在线，但未读取到本地模型。",
        models=models,
    )


def openai_model_id(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, dict):
        return str(item.get("id") or item.get("name") or item.get("model") or "").strip()
    return ""


def detect_openai_compatible_models(provider: LocalModelProvider) -> LocalModelProviderStatus:
    try:
        response = httpx.get(provider.url, timeout=DETECTION_TIMEOUT_SECONDS)
        response.raise_for_status()
        payload = response.json()
    except httpx.RequestError as exc:
        return provider_error_status(provider, f"{provider.name} 未在线或端口不可访问。", str(exc))
    except httpx.HTTPStatusError as exc:
        return provider_error_status(provider, f"{provider.name} 返回 HTTP {exc.response.status_code}。", str(exc))
    except ValueError as exc:
        return provider_error_status(provider, f"{provider.name} 返回内容不是有效 JSON。", str(exc))

    raw_models = payload.get("data") if isinstance(payload, dict) else None
    if raw_models is None and isinstance(payload, dict):
        raw_models = payload.get("models")
    if raw_models is None:
        raw_models = payload if isinstance(payload, list) else []

    models = []
    for item in raw_models or []:
        model_id = openai_model_id(item)
        if not model_id:
            continue
        created = item.get("created") if isinstance(item, dict) else None
        modified_at = str(created) if created is not None else None
        models.append(
            LocalDetectedModel(
                provider_id=provider.id,
                provider=provider.name,
                provider_type=provider.type,
                name=model_id,
                id=model_id,
                modified_at=modified_at,
                can_polish=False,
                recommendation="已检测到；当前版本暂未接入 OpenAI-compatible polish 调用。",
            )
        )
    return LocalModelProviderStatus(
        id=provider.id,
        name=provider.name,
        type=provider.type,
        url=provider.url,
        online=True,
        can_polish=False,
        message=f"检测到 {len(models)} 个模型；当前仅展示，不会用于 polish 调用。"
        if models
        else "服务在线，但 /v1/models 未返回模型。",
        models=models,
    )


def provider_registry() -> list[LocalModelProvider]:
    ollama_base = settings.ollama_base_url.rstrip("/")
    return [
        LocalModelProvider("ollama", "Ollama", "ollama", f"{ollama_base}/api/tags", detect_ollama_models),
        LocalModelProvider("lmstudio", "LM Studio", "openai-compatible", "http://localhost:1234/v1/models", detect_openai_compatible_models),
        LocalModelProvider("llamacpp", "llama.cpp server", "openai-compatible", "http://localhost:8080/v1/models", detect_openai_compatible_models),
        LocalModelProvider("openai8000", "OpenAI-compatible :8000", "openai-compatible", "http://localhost:8000/v1/models", detect_openai_compatible_models),
        LocalModelProvider("openai5000", "OpenAI-compatible :5000", "openai-compatible", "http://localhost:5000/v1/models", detect_openai_compatible_models),
    ]


def detect_local_models() -> LocalModelDetectionStatus:
    providers = [provider.detect(provider) for provider in provider_registry()]
    providers_online = sum(1 for provider in providers if provider.online)
    models_found = sum(len(provider.models) for provider in providers)
    if models_found:
        message = f"检测到 {providers_online} 个在线 provider，{models_found} 个本地模型。"
    else:
        message = "未检测到本地模型服务。请确认 Ollama / LM Studio / llama.cpp server 是否已启动。本功能不会自动下载模型。"
    return LocalModelDetectionStatus(
        checked_at=datetime.now(timezone.utc).isoformat(),
        providers_checked=len(providers),
        providers_online=providers_online,
        models_found=models_found,
        message=message,
        providers=providers,
    )
