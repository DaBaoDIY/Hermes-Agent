from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import os
import tempfile


DEFAULT_CONFIG_PATH = Path(os.environ.get("HERMES_AGENT_CONFIG", "/etc/hermes-agent/config.json"))


DEFAULT_MODELS = [
    {"label": "Amazon Nova Micro", "model_id": "us.amazon.nova-micro-v1:0"},
    {"label": "Amazon Nova Lite", "model_id": "us.amazon.nova-lite-v1:0"},
    {"label": "Amazon Nova Pro", "model_id": "us.amazon.nova-pro-v1:0"},
    {"label": "Amazon Nova Premier", "model_id": "us.amazon.nova-premier-v1:0"},
    {"label": "Amazon Nova 2 Lite", "model_id": "us.amazon.nova-2-lite-v1:0"},
]


@dataclass(slots=True)
class HermesConfig:
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    aws_region: str = "us-east-1"
    model_id: str = "us.amazon.nova-lite-v1:0"
    system_prompt: str = "You are Hermes Agent, a helpful AI operations assistant."
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 1024
    reasoning_enabled: bool = False
    reasoning_effort: str = "low"
    initialized: bool = False
    ui_title: str = "Hermes Agent"
    metadata: dict[str, Any] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["available_models"] = DEFAULT_MODELS
        return payload

    def update_from(self, payload: dict[str, Any]) -> "HermesConfig":
        data = asdict(self)
        allowed = set(data)
        for key, value in payload.items():
            if key in allowed:
                data[key] = value
        return parse_config(data)


def parse_config(payload: dict[str, Any] | None) -> HermesConfig:
    payload = payload or {}
    cfg = HermesConfig()

    def text(name: str, default: str) -> str:
        value = payload.get(name, default)
        if value is None:
            return default
        return str(value).strip() or default

    def integer(name: str, default: int, low: int, high: int) -> int:
        try:
            value = int(payload.get(name, default))
        except (TypeError, ValueError):
            value = default
        return max(low, min(high, value))

    def number(name: str, default: float, low: float, high: float) -> float:
        try:
            value = float(payload.get(name, default))
        except (TypeError, ValueError):
            value = default
        return max(low, min(high, value))

    def boolean(name: str, default: bool) -> bool:
        value = payload.get(name, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in {"1", "true", "yes", "on"}
        return bool(value)

    metadata = payload.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    return HermesConfig(
        bind_host=text("bind_host", cfg.bind_host),
        bind_port=integer("bind_port", cfg.bind_port, 1024, 65535),
        aws_region=text("aws_region", cfg.aws_region),
        model_id=text("model_id", cfg.model_id),
        system_prompt=text("system_prompt", cfg.system_prompt),
        temperature=number("temperature", cfg.temperature, 0.0, 1.0),
        top_p=number("top_p", cfg.top_p, 0.0, 1.0),
        max_tokens=integer("max_tokens", cfg.max_tokens, 1, 65000),
        reasoning_enabled=boolean("reasoning_enabled", cfg.reasoning_enabled),
        reasoning_effort=text("reasoning_effort", cfg.reasoning_effort).lower(),
        initialized=boolean("initialized", cfg.initialized),
        ui_title=text("ui_title", cfg.ui_title),
        metadata=metadata,
    )


def load_config(path: Path | str = DEFAULT_CONFIG_PATH) -> HermesConfig:
    path = Path(path)
    if not path.exists():
        return HermesConfig()
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Configuration at {path} must be a JSON object")
    return parse_config(payload)


def save_config(config: HermesConfig, path: Path | str = DEFAULT_CONFIG_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(asdict(config), indent=2, sort_keys=True)
    fd, tmp_name = tempfile.mkstemp(prefix=".config.", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(payload)
            handle.write("\n")
        os.chmod(tmp_name, 0o660)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
