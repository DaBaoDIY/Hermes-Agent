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
