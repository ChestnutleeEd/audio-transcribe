from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings


class OllamaError(RuntimeError):
    pass


class OllamaUnavailableError(OllamaError):
    pass


class OllamaPullCanceled(OllamaError):
    pass


@dataclass(frozen=True)
class OllamaGenerateResult:
    response: str
    model: str


class OllamaClient:
    def __init__(self, base_url: str | None = None) -> None:
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")

    def api_url(self, path: str) -> str:
        return f"{self.base_url}/api/{path.lstrip('/')}"

    def version(self) -> dict[str, Any]:
        try:
            response = httpx.get(self.api_url("version"), timeout=3)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise OllamaUnavailableError("Ollama 服务不可用，请先启动 Ollama。") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaUnavailableError(f"Ollama 服务返回异常状态：{exc.response.status_code}") from exc

    def list_models(self) -> list[str]:
        try:
            response = httpx.get(self.api_url("tags"), timeout=5)
            response.raise_for_status()
            payload = response.json()
        except httpx.RequestError as exc:
            raise OllamaUnavailableError("Ollama 服务不可用，请先启动 Ollama。") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaUnavailableError(f"Ollama 模型列表读取失败：{exc.response.status_code}") from exc

        names = []
        for item in payload.get("models") or []:
            name = item.get("name") or item.get("model")
            if name:
                names.append(str(name))
        return names

    def model_exists(self, model_id: str) -> bool:
        normalized = normalize_model_name(model_id)
        return any(normalize_model_name(name) == normalized for name in self.list_models())

    def pull_model(
        self,
        model_id: str,
        on_progress: Callable[[str, int | None, int | None], None],
        is_canceled: Callable[[], bool],
    ) -> None:
        try:
            with httpx.stream(
                "POST",
                self.api_url("pull"),
                json={"model": model_id, "stream": True},
                timeout=None,
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if is_canceled():
                        raise OllamaPullCanceled("已取消 Ollama 模型下载")
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except json.JSONDecodeError:
                        on_progress(str(line), None, None)
                        continue
                    if payload.get("error"):
                        raise OllamaError(str(payload["error"]))
                    status = str(payload.get("status") or "下载中")
                    completed = parse_optional_int(payload.get("completed"))
                    total = parse_optional_int(payload.get("total"))
                    on_progress(status, completed, total)
                    if payload.get("done"):
                        return
        except OllamaPullCanceled:
            raise
        except httpx.RequestError as exc:
            raise OllamaUnavailableError("Ollama 服务不可用，请先启动 Ollama。") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Ollama 模型下载失败：HTTP {exc.response.status_code}") from exc

    def generate_text(
        self,
        model_id: str,
        prompt: str,
        response_format: str | dict[str, Any] | None = None,
    ) -> OllamaGenerateResult:
        payload: dict[str, Any] = {
            "model": model_id,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }
        if response_format is not None:
            payload["format"] = response_format
        try:
            response = httpx.post(self.api_url("generate"), json=payload, timeout=180)
            response.raise_for_status()
            data = response.json()
        except httpx.RequestError as exc:
            raise OllamaUnavailableError("Ollama 服务不可用，请先启动 Ollama。") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaError(f"Ollama 文本生成失败：HTTP {exc.response.status_code}") from exc

        if data.get("error"):
            raise OllamaError(str(data["error"]))
        return OllamaGenerateResult(response=str(data.get("response") or ""), model=str(data.get("model") or model_id))


def parse_optional_int(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def normalize_model_name(model_id: str) -> str:
    return model_id if ":" in model_id else f"{model_id}:latest"
