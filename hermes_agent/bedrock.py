from __future__ import annotations

from typing import Any

from .config import HermesConfig


class BedrockUnavailable(RuntimeError):
    pass


def build_converse_request(config: HermesConfig, user_text: str) -> dict[str, Any]:
    request: dict[str, Any] = {
        "modelId": config.model_id,
        "system": [{"text": config.system_prompt}],
        "messages": [
            {
                "role": "user",
                "content": [{"text": user_text}],
            }
        ],
        "inferenceConfig": {
            "maxTokens": config.max_tokens,
            "temperature": config.temperature,
            "topP": config.top_p,
        },
    }

    if config.reasoning_enabled:
        request["additionalModelRequestFields"] = {
            "reasoningConfig": {
                "type": "enabled",
                "maxReasoningEffort": config.reasoning_effort,
            }
        }
    return request


def extract_text(response: dict[str, Any]) -> str:
    chunks = response.get("output", {}).get("message", {}).get("content", [])
    text_parts = [chunk.get("text", "") for chunk in chunks if isinstance(chunk, dict)]
    return "".join(text_parts).strip()


def converse(config: HermesConfig, user_text: str) -> dict[str, Any]:
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise BedrockUnavailable("boto3 is not installed in this environment") from exc

    client = boto3.client(
        "bedrock-runtime",
        region_name=config.aws_region,
        config=Config(
            connect_timeout=60,
            read_timeout=3600,
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )
    request = build_converse_request(config, user_text)
    response = client.converse(**request)
    return {
        "text": extract_text(response),
        "stop_reason": response.get("stopReason"),
        "usage": response.get("usage", {}),
        "metrics": response.get("metrics", {}),
    }
