from hermes_agent.bedrock import build_converse_request, extract_text
from hermes_agent.config import HermesConfig, parse_config


def test_parse_config_clamps_numeric_values():
    config = parse_config(
        {
            "bind_port": "99",
            "temperature": "2",
            "top_p": "-1",
            "max_tokens": "70000",
            "reasoning_enabled": "true",
        }
    )

    assert config.bind_port == 1024
    assert config.temperature == 1.0
    assert config.top_p == 0.0
    assert config.max_tokens == 65000
    assert config.reasoning_enabled is True


def test_build_converse_request_uses_bedrock_converse_shape():
    config = HermesConfig(
        aws_region="us-east-1",
        model_id="us.amazon.nova-lite-v1:0",
        system_prompt="System",
        temperature=0.2,
        top_p=0.8,
        max_tokens=512,
    )

    request = build_converse_request(config, "hello")

    assert request["modelId"] == "us.amazon.nova-lite-v1:0"
    assert request["system"] == [{"text": "System"}]
    assert request["messages"][0]["content"] == [{"text": "hello"}]
    assert request["inferenceConfig"]["maxTokens"] == 512


def test_extract_text_joins_response_chunks():
    response = {
        "output": {
            "message": {
                "content": [
                    {"text": "hello"},
                    {"text": " world"},
                ]
            }
        }
    }

    assert extract_text(response) == "hello world"


def test_external_provider_api_key_is_masked():
    config = parse_config(
        {
            "provider_type": "openai-compatible",
            "api_key": "sk-1234567890",
            "external_providers": [
                {
                    "id": "deepseek",
                    "label": "DeepSeek",
                    "provider_type": "openai-compatible",
                    "model_id": "deepseek-chat",
                    "api_key": "sk-provider-secret",
                }
            ],
        }
    )

    public = config.public_dict()

    assert public["api_key"] == "********7890"
    assert public["external_providers"][0]["api_key"] == "********cret"
    assert public["external_providers"][0]["has_api_key"] is True


def test_mcp_and_skill_runtime_manifests_include_enabled_items():
    config = parse_config(
        {
            "mcp_servers": [
                {
                    "id": "filesystem",
                    "label": "Filesystem",
                    "transport": "stdio",
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"],
                    "env": {"SAFE": "true"},
                    "enabled": True,
                },
                {
                    "id": "disabled",
                    "label": "Disabled",
                    "transport": "http",
                    "url": "https://mcp.example.com",
                    "enabled": False,
                },
            ],
            "skills": [
                {
                    "id": "native-mcp",
                    "label": "Native MCP",
                    "path": "mcp/native-mcp",
                    "category": "MCP",
                    "enabled": True,
                }
            ],
        }
    )

    public = config.public_dict()

    assert "filesystem" in public["mcp_runtime_config"]["mcp_servers"]
    assert "disabled" not in public["mcp_runtime_config"]["mcp_servers"]
    assert public["skills_manifest"] == [
        {"id": "native-mcp", "label": "Native MCP", "path": "mcp/native-mcp", "category": "MCP"}
    ]


def test_public_config_exposes_aws_service_blueprint():
    public = HermesConfig().public_dict()
    service_ids = {item["id"] for item in public["aws_services"]}

    assert {"bedrock", "iam", "api-gateway", "nat-gateway"}.issubset(service_ids)
