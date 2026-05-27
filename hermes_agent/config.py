from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
import json
import os
import tempfile


DEFAULT_CONFIG_PATH = Path(os.environ.get("HERMES_AGENT_CONFIG", "/etc/hermes-agent/config.json"))


DEFAULT_MODELS = [
    {"provider_type": "bedrock", "label": "Amazon Nova Micro", "model_id": "us.amazon.nova-micro-v1:0"},
    {"provider_type": "bedrock", "label": "Amazon Nova Lite", "model_id": "us.amazon.nova-lite-v1:0"},
    {"provider_type": "bedrock", "label": "Amazon Nova Pro", "model_id": "us.amazon.nova-pro-v1:0"},
    {"provider_type": "bedrock", "label": "Amazon Nova Premier", "model_id": "us.amazon.nova-premier-v1:0"},
    {"provider_type": "bedrock", "label": "Amazon Nova 2 Lite", "model_id": "us.amazon.nova-2-lite-v1:0"},
    {"provider_type": "bedrock", "label": "Anthropic Claude Sonnet 4.6", "model_id": "anthropic.claude-sonnet-4-6"},
    {"provider_type": "bedrock", "label": "DeepSeek R1", "model_id": "deepseek.r1-v1:0"},
    {"provider_type": "bedrock", "label": "DeepSeek V3.2", "model_id": "deepseek.v3.2"},
    {"provider_type": "bedrock", "label": "Moonshot Kimi K2 Thinking", "model_id": "moonshot.kimi-k2-thinking"},
    {"provider_type": "bedrock", "label": "Google Gemma 3 27B IT", "model_id": "google.gemma-3-27b-it"},
    {"provider_type": "bedrock", "label": "OpenAI GPT OSS", "model_id": "openai.gpt-oss-120b-1:0"},
    {"provider_type": "anthropic", "label": "Claude Sonnet 4.5 API", "model_id": "claude-sonnet-4-5"},
    {"provider_type": "google-gemini", "label": "Gemini 2.5 Flash API", "model_id": "gemini-2.5-flash"},
    {"provider_type": "openai-compatible", "label": "DeepSeek Chat API", "model_id": "deepseek-chat"},
    {"provider_type": "openai-compatible", "label": "Kimi K2 API", "model_id": "kimi-k2-0711-preview"},
]


PROVIDER_TYPES = [
    {
        "id": "bedrock",
        "label": "Amazon Bedrock",
        "auth": "iam",
        "base_url": "",
        "description": "Uses the EC2 instance profile or AWS credential chain.",
    },
    {
        "id": "openai-compatible",
        "label": "OpenAI Compatible",
        "auth": "api_key",
        "base_url": "https://api.openai.com/v1",
        "description": "Works with OpenAI, OpenRouter, DeepSeek, Kimi, Together, vLLM, LM Studio, and other /v1/chat/completions APIs.",
    },
    {
        "id": "anthropic",
        "label": "Anthropic API",
        "auth": "api_key",
        "base_url": "https://api.anthropic.com/v1",
        "description": "Native Anthropic Messages API for Claude models.",
    },
    {
        "id": "google-gemini",
        "label": "Google Gemini API",
        "auth": "api_key",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "description": "Native Gemini generateContent API.",
    },
]


AWS_SERVICE_PRESETS = [
    {
        "id": "bedrock",
        "label": "Amazon Bedrock",
        "layer": "AI Model",
        "layer_zh": "AI 模型",
        "status": "active",
        "description": "Primary managed foundation-model runtime through the Bedrock Converse API.",
        "description_zh": "默认托管基础模型运行时，通过 Bedrock Converse API 提供模型调用能力。",
    },
    {
        "id": "iam",
        "label": "AWS IAM",
        "layer": "Identity",
        "layer_zh": "身份权限",
        "status": "active",
        "description": "EC2 instance profile and least-privilege Bedrock invocation policy.",
        "description_zh": "使用 EC2 instance profile 和最小权限策略调用 Bedrock。",
    },
    {
        "id": "ec2",
        "label": "Amazon EC2",
        "layer": "Compute",
        "layer_zh": "计算",
        "status": "active",
        "description": "Rocky Linux runtime host for the Hermes Agent web UI and provider bridge.",
        "description_zh": "承载 Hermes Agent Web UI、systemd 服务和模型调用桥接进程。",
    },
    {
        "id": "vpc",
        "label": "Amazon VPC",
        "layer": "Network",
        "layer_zh": "网络",
        "status": "active",
        "description": "Security group controlled ingress, private subnet option, and outbound routing.",
        "description_zh": "通过安全组控制入口，可扩展到私有子网与统一出站路由。",
    },
    {
        "id": "api-gateway",
        "label": "Amazon API Gateway",
        "layer": "Edge",
        "layer_zh": "托管入口",
        "status": "optional",
        "description": "Optional HTTP API front door for exposing Hermes Agent over a managed HTTPS endpoint.",
        "description_zh": "可选 HTTP API 前门，用托管 HTTPS 入口暴露 Hermes Agent。",
    },
    {
        "id": "nat-gateway",
        "label": "NAT Gateway",
        "layer": "Network",
        "layer_zh": "网络",
        "status": "optional",
        "description": "Optional private-subnet egress path for Bedrock, package downloads, and MCP endpoints.",
        "description_zh": "可选私有子网出站路径，用于访问 Bedrock、公网模型 API 和远程 MCP endpoint。",
    },
    {
        "id": "systems-manager",
        "label": "AWS Systems Manager",
        "layer": "Operations",
        "layer_zh": "运维",
        "status": "active",
        "description": "Session Manager access and remote setup token retrieval without opening SSH broadly.",
        "description_zh": "支持 Session Manager 和远程获取 setup token，减少 SSH 暴露面。",
    },
    {
        "id": "cloudwatch",
        "label": "Amazon CloudWatch",
        "layer": "Operations",
        "layer_zh": "运维",
        "status": "planned",
        "description": "Recommended target for service logs, metrics, alarms, and operational dashboards.",
        "description_zh": "建议作为生产日志、指标、告警和运维看板的统一目标。",
    },
    {
        "id": "secrets-manager",
        "label": "AWS Secrets Manager",
        "layer": "Security",
        "layer_zh": "安全",
        "status": "planned",
        "description": "Recommended external provider API-key storage for production deployments.",
        "description_zh": "建议在生产环境集中托管外部模型 API key。",
    },
]


MCP_PRESETS = [
    {
        "id": "filesystem",
        "label": "Filesystem",
        "category": "Core",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/opt/hermes-agent/workspace"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "Node.js 20+, workspace directory",
        "description": "Expose a controlled workspace directory to MCP tools.",
    },
    {
        "id": "github",
        "label": "GitHub",
        "category": "Code",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": ""},
        "enabled": False,
        "popular": True,
        "requirements": "GitHub token",
        "description": "Repository, issue, PR, and code search tools.",
    },
    {
        "id": "git",
        "label": "Git",
        "category": "Code",
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-git", "--repository", "/opt/hermes-agent/workspace"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "uv, local git repository",
        "description": "Inspect branches, commits, diffs, and repository state.",
    },
    {
        "id": "fetch",
        "label": "Fetch",
        "category": "Web",
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-fetch"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "uv, outbound HTTPS",
        "description": "Fetch web pages and convert them into model-readable content.",
    },
    {
        "id": "memory",
        "label": "Memory",
        "category": "Knowledge",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-memory"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "Node.js 20+",
        "description": "Persistent graph-style memory for entities, notes, and relationships.",
    },
    {
        "id": "sequential-thinking",
        "label": "Sequential Thinking",
        "category": "Reasoning",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "Node.js 20+",
        "description": "Structured multi-step reasoning and plan refinement.",
    },
    {
        "id": "time",
        "label": "Time",
        "category": "Utility",
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-time", "--local-timezone=Asia/Shanghai"],
        "env": {},
        "enabled": False,
        "popular": False,
        "requirements": "uv",
        "description": "Timezone-aware current time and date conversion tools.",
    },
    {
        "id": "postgres",
        "label": "PostgreSQL",
        "category": "Data",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://user:pass@host:5432/db"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "PostgreSQL connection string",
        "description": "Read-only database exploration and query workflows.",
    },
    {
        "id": "sqlite",
        "label": "SQLite",
        "category": "Data",
        "transport": "stdio",
        "command": "uvx",
        "args": ["mcp-server-sqlite", "--db-path", "/opt/hermes-agent/workspace/app.db"],
        "env": {},
        "enabled": False,
        "popular": False,
        "requirements": "uv, SQLite database file",
        "description": "Explore and query a local SQLite database.",
    },
    {
        "id": "brave-search",
        "label": "Brave Search",
        "category": "Web",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "env": {"BRAVE_API_KEY": ""},
        "enabled": False,
        "popular": True,
        "requirements": "Brave Search API key",
        "description": "Web search for research, troubleshooting, and citation discovery.",
    },
    {
        "id": "browser",
        "label": "Playwright Browser",
        "category": "Browser",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@playwright/mcp@latest"],
        "env": {},
        "enabled": False,
        "popular": True,
        "requirements": "Node.js 20+, browser dependencies",
        "description": "Browser inspection, navigation, screenshots, and UI testing.",
    },
    {
        "id": "puppeteer",
        "label": "Puppeteer Browser",
        "category": "Browser",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {},
        "enabled": False,
        "popular": False,
        "requirements": "Node.js 20+, browser dependencies",
        "description": "Alternative browser automation server for page control and screenshots.",
    },
    {
        "id": "slack",
        "label": "Slack",
        "category": "Collaboration",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "env": {"SLACK_BOT_TOKEN": "", "SLACK_TEAM_ID": ""},
        "enabled": False,
        "popular": False,
        "requirements": "Slack bot token and team ID",
        "description": "Read channels and post messages for collaboration workflows.",
    },
    {
        "id": "google-drive",
        "label": "Google Drive",
        "category": "Documents",
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-gdrive"],
        "env": {"GDRIVE_CREDENTIALS_PATH": "/etc/hermes-agent/gdrive-credentials.json"},
        "enabled": False,
        "popular": False,
        "requirements": "Google OAuth credentials",
        "description": "Search and read documents from Google Drive.",
    },
    {
        "id": "aws-docs",
        "label": "AWS Docs",
        "category": "Cloud",
        "transport": "http",
        "url": "https://knowledge-mcp.global.api.aws",
        "headers": {},
        "enabled": False,
        "popular": True,
        "requirements": "Outbound HTTPS",
        "description": "AWS documentation and best-practice lookup through a hosted MCP endpoint.",
    },
    {
        "id": "remote-http",
        "label": "Remote HTTP MCP",
        "category": "Custom",
        "transport": "http",
        "url": "https://mcp.example.com",
        "headers": {"Authorization": "Bearer "},
        "enabled": False,
        "popular": False,
        "requirements": "Hosted MCP URL and optional token",
        "description": "Template for hosted MCP endpoints.",
    },
]


SKILL_PRESETS = [
    {
        "id": "native-mcp",
        "label": "Native MCP",
        "category": "MCP",
        "path": "mcp/native-mcp",
        "enabled": True,
        "popular": True,
        "description": "Connect stdio and HTTP MCP servers and register tools.",
    },
    {
        "id": "systematic-debugging",
        "label": "Systematic Debugging",
        "category": "Engineering",
        "path": "software-development/systematic-debugging",
        "enabled": True,
        "popular": True,
        "description": "Structured root-cause debugging workflow.",
    },
    {
        "id": "test-driven-development",
        "label": "Test Driven Development",
        "category": "Engineering",
        "path": "software-development/test-driven-development",
        "enabled": False,
        "popular": True,
        "description": "RED-GREEN-REFACTOR implementation workflow.",
    },
    {
        "id": "requesting-code-review",
        "label": "Code Review",
        "category": "Engineering",
        "path": "software-development/requesting-code-review",
        "enabled": False,
        "popular": True,
        "description": "Pre-commit review and quality gates.",
    },
    {
        "id": "frontend-ux",
        "label": "Frontend UX",
        "category": "Frontend",
        "path": "software-development/frontend-ux",
        "enabled": False,
        "popular": True,
        "description": "Frontend implementation, responsive QA, accessibility, and visual polish.",
    },
    {
        "id": "aws-bedrock",
        "label": "AWS Bedrock",
        "category": "Cloud",
        "path": "cloud/aws-bedrock",
        "enabled": True,
        "popular": True,
        "description": "Model access, IAM policy, Converse API, and inference profile guidance.",
    },
    {
        "id": "terraform-iac",
        "label": "Terraform IaC",
        "category": "Cloud",
        "path": "cloud/terraform-iac",
        "enabled": False,
        "popular": True,
        "description": "Infrastructure modules, review, plan validation, and safe deployment patterns.",
    },
    {
        "id": "docker-kubernetes",
        "label": "Docker and Kubernetes",
        "category": "Cloud",
        "path": "platform/docker-kubernetes",
        "enabled": False,
        "popular": False,
        "description": "Container packaging, Kubernetes manifests, and runtime troubleshooting.",
    },
    {
        "id": "rag-knowledge-base",
        "label": "RAG Knowledge Base",
        "category": "AI",
        "path": "mlops/rag-knowledge-base",
        "enabled": False,
        "popular": True,
        "description": "Chunking, embedding, retrieval, reranking, and evaluation workflows.",
    },
    {
        "id": "serving-llms-vllm",
        "label": "Serving LLMs with vLLM",
        "category": "AI",
        "path": "mlops/serving-llms-vllm",
        "enabled": False,
        "popular": False,
        "description": "Self-hosted model serving, OpenAI-compatible endpoints, and performance tuning.",
    },
    {
        "id": "dspy",
        "label": "DSPy",
        "category": "AI",
        "path": "mlops/research/dspy",
        "enabled": False,
        "popular": False,
        "description": "Declarative LLM programs, prompt optimization, and RAG.",
    },
    {
        "id": "huggingface-hub",
        "label": "Hugging Face Hub",
        "category": "AI",
        "path": "mlops/huggingface-hub",
        "enabled": False,
        "popular": False,
        "description": "Search, download, and upload models and datasets.",
    },
    {
        "id": "documents",
        "label": "Documents",
        "category": "Productivity",
        "path": "productivity/documents",
        "enabled": False,
        "popular": True,
        "description": "Create, review, and render Word-style documents.",
    },
    {
        "id": "spreadsheets",
        "label": "Spreadsheets",
        "category": "Productivity",
        "path": "productivity/spreadsheets",
        "enabled": False,
        "popular": True,
        "description": "Analyze, transform, and generate spreadsheet workbooks.",
    },
    {
        "id": "presentations",
        "label": "Presentations",
        "category": "Productivity",
        "path": "productivity/presentations",
        "enabled": False,
        "popular": False,
        "description": "Build and verify slide decks.",
    },
]


@dataclass(slots=True)
class HermesConfig:
    bind_host: str = "0.0.0.0"
    bind_port: int = 8080
    aws_region: str = "us-east-1"
    provider_type: str = "bedrock"
    provider_label: str = "Amazon Bedrock"
    base_url: str = ""
    api_key: str = ""
    model_id: str = "us.amazon.nova-lite-v1:0"
    system_prompt: str = "You are Hermes Agent, a helpful AI operations assistant."
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 1024
    reasoning_enabled: bool = False
    reasoning_effort: str = "low"
    initialized: bool = False
    ui_title: str = "Hermes Agent"
    external_providers: list[dict[str, Any]] = field(default_factory=list)
    mcp_servers: list[dict[str, Any]] = field(default_factory=list)
    skills: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def public_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["api_key"] = mask_secret(self.api_key)
        payload["external_providers"] = [mask_provider(provider) for provider in self.external_providers]
        payload["available_models"] = DEFAULT_MODELS
        payload["provider_types"] = PROVIDER_TYPES
        payload["aws_services"] = AWS_SERVICE_PRESETS
        payload["mcp_presets"] = MCP_PRESETS
        payload["skill_presets"] = SKILL_PRESETS
        payload["enabled_mcp_servers"] = [item for item in self.mcp_servers if item.get("enabled")]
        payload["enabled_skills"] = [item for item in self.skills if item.get("enabled")]
        payload["mcp_runtime_config"] = build_mcp_runtime_config(self.mcp_servers)
        payload["skills_manifest"] = build_skills_manifest(self.skills)
        return payload

    def update_from(self, payload: dict[str, Any]) -> "HermesConfig":
        data = asdict(self)
        allowed = set(data)
        for key, value in payload.items():
            if key in allowed:
                if key == "api_key" and is_masked_secret(value):
                    continue
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
    external_providers = sanitize_providers(payload.get("external_providers", []))
    mcp_servers = sanitize_named_items(payload.get("mcp_servers", []))
    skills = sanitize_named_items(payload.get("skills", []))

    return HermesConfig(
        bind_host=text("bind_host", cfg.bind_host),
        bind_port=integer("bind_port", cfg.bind_port, 1024, 65535),
        aws_region=text("aws_region", cfg.aws_region),
        provider_type=text("provider_type", cfg.provider_type),
        provider_label=text("provider_label", cfg.provider_label),
        base_url=text("base_url", cfg.base_url),
        api_key=text("api_key", cfg.api_key),
        model_id=text("model_id", cfg.model_id),
        system_prompt=text("system_prompt", cfg.system_prompt),
        temperature=number("temperature", cfg.temperature, 0.0, 1.0),
        top_p=number("top_p", cfg.top_p, 0.0, 1.0),
        max_tokens=integer("max_tokens", cfg.max_tokens, 1, 65000),
        reasoning_enabled=boolean("reasoning_enabled", cfg.reasoning_enabled),
        reasoning_effort=text("reasoning_effort", cfg.reasoning_effort).lower(),
        initialized=boolean("initialized", cfg.initialized),
        ui_title=text("ui_title", cfg.ui_title),
        external_providers=external_providers,
        mcp_servers=mcp_servers,
        skills=skills,
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


def is_masked_secret(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("********")


def mask_secret(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "********"
    return f"********{value[-4:]}"


def mask_provider(provider: dict[str, Any]) -> dict[str, Any]:
    masked = dict(provider)
    if "api_key" in masked:
        masked["api_key"] = mask_secret(str(masked.get("api_key", "")))
        masked["has_api_key"] = bool(provider.get("api_key"))
    return masked


def sanitize_providers(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    providers: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        provider = {
            "id": str(item.get("id", "")).strip(),
            "label": str(item.get("label", "")).strip(),
            "provider_type": str(item.get("provider_type", "openai-compatible")).strip(),
            "model_id": str(item.get("model_id", "")).strip(),
            "aws_region": str(item.get("aws_region", "")).strip(),
            "base_url": str(item.get("base_url", "")).strip(),
            "api_key": str(item.get("api_key", "")).strip(),
            "enabled": bool(item.get("enabled", True)),
        }
        if provider["id"] and provider["label"]:
            providers.append(provider)
    return providers


def sanitize_named_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    items: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            continue
        item_id = str(item.get("id", "")).strip()
        label = str(item.get("label", item_id)).strip()
        if item_id and label:
            clean = dict(item)
            clean["id"] = item_id
            clean["label"] = label
            clean["enabled"] = bool(item.get("enabled", False))
            items.append(clean)
    return items


def build_mcp_runtime_config(items: list[dict[str, Any]]) -> dict[str, Any]:
    servers: dict[str, Any] = {}
    for item in items:
        if not item.get("enabled"):
            continue
        server: dict[str, Any] = {"transport": item.get("transport", "stdio")}
        if item.get("transport") == "http":
            server["url"] = item.get("url", "")
            headers = item.get("headers", {})
            if headers:
                server["headers"] = headers
        else:
            server["command"] = item.get("command", "")
            server["args"] = item.get("args", [])
            env = item.get("env", {})
            if env:
                server["env"] = env
        servers[str(item["id"])] = server
    return {"mcp_servers": servers}


def build_skills_manifest(items: list[dict[str, Any]]) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for item in items:
        if item.get("enabled"):
            manifest.append(
                {
                    "id": str(item.get("id", "")),
                    "label": str(item.get("label", "")),
                    "path": str(item.get("path", "")),
                    "category": str(item.get("category", "")),
                }
            )
    return manifest
