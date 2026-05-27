from __future__ import annotations

from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

from .bedrock import converse as bedrock_converse
from .config import HermesConfig


class ProviderError(RuntimeError):
    pass


def converse(config: HermesConfig, user_text: str) -> dict[str, Any]:
    provider_type = config.provider_type
    if provider_type == "bedrock":
        return bedrock_converse(config, user_text)
    if provider_type == "openai-compatible":
        return openai_compatible_converse(config, user_text)
    if provider_type == "anthropic":
        return anthropic_converse(config, user_text)
    if provider_type == "google-gemini":
        return gemini_converse(config, user_text)
    raise ProviderError(f"Unsupported provider type: {provider_type}")


def openai_compatible_converse(config: HermesConfig, user_text: str) -> dict[str, Any]:
    require_api_key(config)
    base_url = (config.base_url or "https://api.openai.com/v1").rstrip("/")
    payload = {
        "model": config.model_id,
        "messages": [
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": user_text},
        ],
        "temperature": config.temperature,
        "top_p": config.top_p,
        "max_tokens": config.max_tokens,
    }
    data = request_json(
        f"{base_url}/chat/completions",
        payload,
        {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        },
    )
    choice = (data.get("choices") or [{}])[0]
    message = choice.get("message", {})
    return {
        "text": str(message.get("content", "")).strip(),
        "stop_reason": choice.get("finish_reason"),
        "usage": data.get("usage", {}),
        "metrics": {},
    }


def anthropic_converse(config: HermesConfig, user_text: str) -> dict[str, Any]:
    require_api_key(config)
    base_url = (config.base_url or "https://api.anthropic.com/v1").rstrip("/")
    payload = {
        "model": config.model_id,
        "max_tokens": config.max_tokens,
        "temperature": config.temperature,
        "top_p": config.top_p,
        "system": config.system_prompt,
        "messages": [{"role": "user", "content": user_text}],
    }
    data = request_json(
        f"{base_url}/messages",
        payload,
        {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
    )
    text = "".join(chunk.get("text", "") for chunk in data.get("content", []) if isinstance(chunk, dict))
    return {
        "text": text.strip(),
        "stop_reason": data.get("stop_reason"),
        "usage": data.get("usage", {}),
        "metrics": {},
    }


def gemini_converse(config: HermesConfig, user_text: str) -> dict[str, Any]:
    require_api_key(config)
    base_url = (config.base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")
    payload = {
        "systemInstruction": {"parts": [{"text": config.system_prompt}]},
        "contents": [{"role": "user", "parts": [{"text": user_text}]}],
        "generationConfig": {
            "temperature": config.temperature,
            "topP": config.top_p,
            "maxOutputTokens": config.max_tokens,
        },
    }
    data = request_json(
        f"{base_url}/models/{config.model_id}:generateContent?key={config.api_key}",
        payload,
        {"Content-Type": "application/json"},
    )
    candidates = data.get("candidates") or []
    parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
    text = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    return {
        "text": text.strip(),
        "stop_reason": candidates[0].get("finishReason") if candidates else None,
        "usage": data.get("usageMetadata", {}),
        "metrics": {},
    }


def require_api_key(config: HermesConfig) -> None:
    if not config.api_key:
        raise ProviderError("API key is required for this provider")


def request_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, headers=headers, method="POST")
    try:
        with urlopen(request, timeout=120) as response:
            data = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise ProviderError(f"Provider HTTP {exc.code}: {message}") from exc
    except URLError as exc:
        raise ProviderError(f"Provider request failed: {exc.reason}") from exc
    if not isinstance(data, dict):
        raise ProviderError("Provider response must be a JSON object")
    return data
