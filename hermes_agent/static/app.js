const i18n = {
  zh: {
    activeModel: "当前模型",
    architecture: "AWS 架构",
    architectureSubtitle: "当前部署以 EC2 + IAM + Bedrock 为核心，可按生产网络标准接入 API Gateway、NAT、CloudWatch 与 Secrets Manager。",
    architectureTitle: "云原生部署视图",
    baseUrl: "Base URL",
    chat: "对话",
    clear: "清空",
    configSaved: "配置已保存",
    configPreview: "配置预览",
    connect: "连接",
    connecting: "连接中",
    consoleSubtitle: "统一配置模型、MCP、skills 与可视化操作入口。",
    consoleTitle: "智能体控制台",
    addCustom: "添加自定义",
    argsHint: "空格分隔参数",
    category: "分类",
    commandOrUrl: "Command / URL",
    copy: "复制",
    copied: "已复制",
    description: "描述",
    displayName: "显示名称",
    envHint: "KEY=value,KEY2=value2",
    filter: "筛选",
    importUse: "导入并使用",
    mcpHeroHint: "从预置库启用常用 MCP 和 skills，也可以添加企业内部 MCP endpoint 或本地 skill。",
    mcpHeroTitle: "能力中心",
    mcpHint: "支持 stdio 和 HTTP 两类 MCP 接入。",
    mcpSkills: "MCP 与 Skills",
    messagePlaceholder: "输入消息",
    modelId: "模型 ID",
    modelPreset: "模型预设",
    offline: "离线",
    providerHint: "Bedrock 使用 IAM；外部提供商可导入 API key。",
    providers: "模型接入",
    providerType: "提供商类型",
    refresh: "刷新",
    runtimeConfig: "运行配置",
    save: "保存",
    saveConfig: "保存配置",
    send: "发送",
    skillsHint: "预置工程、云、AI、文档与数据分析类常用 skills。",
    setupSubtitle: "输入实例首次启动生成的 setup token 进入控制台。",
    setupTitle: "VSTECS Hermes Agent 控制台",
    setupToken: "Setup Token",
    systemPrompt: "系统提示词",
    testModel: "测试模型",
    ready: "已就绪",
    tokenRequired: "需要 Setup Token",
    pendingSetup: "待初始化",
    optional: "可选",
    planned: "规划",
    active: "已启用",
  },
  en: {
    activeModel: "Active model",
    architecture: "AWS Architecture",
    architectureSubtitle: "The current deployment is centered on EC2, IAM, and Bedrock, with production-ready paths for API Gateway, NAT, CloudWatch, and Secrets Manager.",
    architectureTitle: "Cloud Deployment View",
    baseUrl: "Base URL",
    chat: "Chat",
    clear: "Clear",
    configSaved: "Configuration saved",
    configPreview: "Config preview",
    connect: "Connect",
    connecting: "Connecting",
    consoleSubtitle: "Configure models, MCP, skills, and visual operations in one place.",
    consoleTitle: "Agent Console",
    addCustom: "Add custom",
    argsHint: "Space-separated arguments",
    category: "Category",
    commandOrUrl: "Command / URL",
    copy: "Copy",
    copied: "Copied",
    description: "Description",
    displayName: "Display name",
    envHint: "KEY=value,KEY2=value2",
    filter: "Filter",
    importUse: "Import and use",
    mcpHeroHint: "Enable popular MCP servers and skills from presets, or add internal MCP endpoints and local skills.",
    mcpHeroTitle: "Capability Hub",
    mcpHint: "Supports stdio and HTTP MCP integrations.",
    mcpSkills: "MCP and Skills",
    messagePlaceholder: "Type a message",
    modelId: "Model ID",
    modelPreset: "Model preset",
    offline: "Offline",
    providerHint: "Bedrock uses IAM. External providers can be imported with API keys.",
    providers: "Model providers",
    providerType: "Provider type",
    refresh: "Refresh",
    runtimeConfig: "Runtime config",
    save: "Save",
    saveConfig: "Save config",
    send: "Send",
    skillsHint: "Presets for engineering, cloud, AI, document, and data analysis workflows.",
    setupSubtitle: "Enter the setup token generated on first boot to open the console.",
    setupTitle: "VSTECS Hermes Agent Console",
    setupToken: "Setup Token",
    systemPrompt: "System prompt",
    testModel: "Test model",
    ready: "Ready",
    tokenRequired: "Setup token required",
    pendingSetup: "Pending setup",
    optional: "Optional",
    planned: "Planned",
    active: "Active",
  },
};

const state = {
  setupToken: localStorage.getItem("hermes-token") || "",
  lang: localStorage.getItem("hermes-lang") || "zh",
  theme: localStorage.getItem("hermes-theme") || "dark",
  config: null,
  sending: false,
};

const $ = (id) => document.getElementById(id);
const t = (key) => (i18n[state.lang] && i18n[state.lang][key]) || i18n.zh[key] || key;

function headers() {
  const base = { "Content-Type": "application/json" };
  if (state.setupToken) base["X-Hermes-Token"] = state.setupToken;
  return base;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.error || `HTTP ${response.status}`);
  }
  return payload;
}

function applyI18n() {
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  for (const el of document.querySelectorAll("[data-i18n]")) {
    el.textContent = t(el.dataset.i18n);
  }
  for (const el of document.querySelectorAll("[data-i18n-placeholder]")) {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  }
  $("lang-toggle").textContent = state.lang === "zh" ? "EN" : "中";
}

function applyTheme() {
  document.documentElement.dataset.theme = state.theme;
  $("theme-toggle").textContent = state.theme === "dark" ? "☼" : "◐";
}

function toast(message) {
  const box = $("toast");
  box.textContent = message;
  box.classList.remove("hidden");
  window.clearTimeout(box._timer);
  box._timer = window.setTimeout(() => box.classList.add("hidden"), 4200);
}

function setStatus(kind, text) {
  $("status-dot").className = `dot ${kind || ""}`;
  $("status-text").textContent = text;
}

function showSetupPanel(show) {
  $("setup-panel").classList.toggle("hidden", !show);
  $("app-view").classList.toggle("dimmed", show);
}

function showSection(sectionId) {
  for (const section of document.querySelectorAll(".content-section")) {
    section.classList.toggle("hidden", section.id !== sectionId);
  }
  for (const item of document.querySelectorAll(".side-item")) {
    item.classList.toggle("active", item.dataset.section === sectionId);
  }
}

function readForm() {
  return {
    provider_type: $("provider_type").value,
    aws_region: $("aws_region").value.trim(),
    base_url: $("base_url").value.trim(),
    api_key: $("api_key").value.trim(),
    model_id: $("model_id").value.trim(),
    system_prompt: $("system_prompt").value,
    temperature: Number($("temperature").value),
    top_p: Number($("top_p").value),
    max_tokens: Number($("max_tokens").value),
    reasoning_enabled: $("reasoning_enabled").checked,
    reasoning_effort: $("reasoning_effort").value,
  };
}

function fillForm(config) {
  state.config = config;
  fillProviderTypes("provider_type", config.provider_type);
  fillProviderTypes("provider-import-type", "openai-compatible");

  $("aws_region").value = config.aws_region || "";
  $("base_url").value = config.base_url || "";
  $("api_key").value = config.api_key || "";
  $("model_id").value = config.model_id || "";
  $("system_prompt").value = config.system_prompt || "";
  $("temperature").value = config.temperature ?? 0.3;
  $("top_p").value = config.top_p ?? 0.9;
  $("max_tokens").value = config.max_tokens ?? 1024;
  $("reasoning_enabled").checked = Boolean(config.reasoning_enabled);
  $("reasoning_effort").value = config.reasoning_effort || "low";

  const preset = $("model-preset");
  preset.innerHTML = "";
  for (const item of config.available_models || []) {
    const option = document.createElement("option");
    option.value = item.model_id;
    option.dataset.providerType = item.provider_type;
    option.textContent = `${item.label} · ${item.provider_type}`;
    preset.appendChild(option);
  }
  const custom = document.createElement("option");
  custom.value = "";
  custom.textContent = "Custom";
  preset.appendChild(custom);
  preset.value = [...preset.options].some((option) => option.value === config.model_id) ? config.model_id : "";

  $("active-model-title").textContent = `${config.provider_label || config.provider_type} · ${config.model_id}`;
  $("hero-provider").textContent = config.provider_label || providerTypeLabel(config.provider_type);
  renderAwsArchitecture(config);
  renderProviders(config);
  renderMcp(config);
  renderSkills(config);
}

function fillProviderTypes(selectId, current) {
  const select = $(selectId);
  select.innerHTML = "";
  for (const item of state.config?.provider_types || defaultProviderTypes()) {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.label;
    select.appendChild(option);
  }
  select.value = current || "bedrock";
}

function defaultProviderTypes() {
  return [
    { id: "bedrock", label: "Amazon Bedrock" },
    { id: "openai-compatible", label: "OpenAI Compatible" },
    { id: "anthropic", label: "Anthropic API" },
    { id: "google-gemini", label: "Google Gemini API" },
  ];
}

function providerTypeLabel(id) {
  return (state.config?.provider_types || defaultProviderTypes()).find((item) => item.id === id)?.label || id;
}

function defaultAwsServices() {
  return [
    {
      id: "bedrock",
      label: "Amazon Bedrock",
      layer: "AI Model",
      status: "active",
      description: "Managed foundation-model runtime through the Bedrock Converse API.",
    },
    {
      id: "iam",
      label: "AWS IAM",
      layer: "Identity",
      status: "active",
      description: "Instance profile and least-privilege Bedrock invocation policy.",
    },
    {
      id: "ec2",
      label: "Amazon EC2",
      layer: "Compute",
      status: "active",
      description: "Rocky Linux runtime host for Hermes Agent.",
    },
    {
      id: "api-gateway",
      label: "Amazon API Gateway",
      layer: "Edge",
      status: "optional",
      description: "Optional managed HTTPS entry point for production exposure.",
    },
    {
      id: "nat-gateway",
      label: "NAT Gateway",
      layer: "Network",
      status: "optional",
      description: "Optional private-subnet outbound path.",
    },
  ];
}

function serviceStatusLabel(status) {
  if (status === "active") return t("active");
  if (status === "planned") return t("planned");
  return t("optional");
}

function renderAwsArchitecture(config) {
  const list = $("aws-service-list");
  if (!list) return;
  list.innerHTML = "";
  for (const service of config.aws_services || defaultAwsServices()) {
    const card = document.createElement("article");
    card.className = `service-card ${service.status || "optional"}`;
    card.innerHTML = `
      <div class="service-card-top">
        <span class="service-layer"></span>
        <span class="service-status"></span>
      </div>
      <strong></strong>
      <p></p>
    `;
    card.querySelector(".service-layer").textContent = state.lang === "zh" ? service.layer_zh || service.layer || "AWS" : service.layer || "AWS";
    card.querySelector(".service-status").textContent = serviceStatusLabel(service.status);
    card.querySelector("strong").textContent = service.label;
    card.querySelector("p").textContent = state.lang === "zh" ? service.description_zh || service.description || "" : service.description || "";
    list.appendChild(card);
  }

  const nodes = $("aws-flow-nodes");
  if (nodes) {
    const flow = [
      "Client",
      "API Gateway",
      "Security Group",
      "EC2 / Rocky Linux",
      "IAM Role",
      "Amazon Bedrock",
      "CloudWatch",
    ];
    nodes.innerHTML = "";
    flow.forEach((label, index) => {
      const item = document.createElement("span");
      item.textContent = label;
      item.style.setProperty("--step", String(index));
      nodes.appendChild(item);
    });
  }
}

function renderProviders(config) {
  const list = $("provider-list");
  list.innerHTML = "";
  const active = {
    id: "active",
    label: config.provider_label || providerTypeLabel(config.provider_type),
    provider_type: config.provider_type,
    model_id: config.model_id,
    base_url: config.base_url,
    aws_region: config.aws_region,
  };
  for (const provider of [active, ...(config.external_providers || [])]) {
    const row = document.createElement("div");
    row.className = "list-item";
    row.innerHTML = `
      <input type="radio" ${provider.model_id === config.model_id && provider.provider_type === config.provider_type ? "checked" : ""} />
      <div>
        <strong></strong>
        <small></small>
      </div>
      <button type="button" class="ghost">${t("runtimeConfig")}</button>
    `;
    row.querySelector("strong").textContent = provider.label || providerTypeLabel(provider.provider_type);
    row.querySelector("small").textContent = `${providerTypeLabel(provider.provider_type)} · ${provider.model_id || ""}`;
    row.querySelector("button").addEventListener("click", async () => {
      if (provider.id === "active") {
        showSection("config-section");
        return;
      }
      const config = await api("/api/providers/use", { method: "POST", body: JSON.stringify({ id: provider.id }) });
      fillForm(config);
      toast(t("configSaved"));
    });
    list.appendChild(row);
  }
}

function renderMcp(config) {
  const selected = new Map((config.mcp_servers || []).map((item) => [item.id, item]));
  const items = mergePresetState(config.mcp_presets || [], selected);
  const list = $("mcp-list");
  list.innerHTML = "";
  for (const item of items) {
    list.appendChild(renderToggleItem(item, "mcp"));
  }
  applyIntegrationFilters();
  updateIntegrationPreview();
}

function renderSkills(config) {
  const selected = new Map((config.skills || []).map((item) => [item.id, item]));
  const items = mergePresetState(config.skill_presets || [], selected);
  const list = $("skills-list");
  list.innerHTML = "";
  for (const item of items) {
    list.appendChild(renderToggleItem(item, "skill"));
  }
  applyIntegrationFilters();
  updateIntegrationPreview();
}

function mergePresetState(presets, selected) {
  return presets.map((item) => ({ ...item, ...(selected.get(item.id) || {}) }));
}

function renderToggleItem(item, type) {
  const row = document.createElement("label");
  row.className = "list-item capability-card";
  row.innerHTML = `
    <input type="checkbox" />
    <div>
      <div class="capability-title">
        <strong></strong>
        <span class="badge"></span>
      </div>
      <small></small>
      <code></code>
    </div>
    <span class="hint pill"></span>
  `;
  row.dataset.type = type;
  row.dataset.search = `${item.label || ""} ${item.category || ""} ${item.description || ""} ${item.path || ""} ${item.command || ""} ${item.transport || ""}`.toLowerCase();
  row.dataset.item = JSON.stringify(item);
  const input = row.querySelector("input");
  input.checked = Boolean(item.enabled);
  input.addEventListener("change", updateIntegrationPreview);
  row.querySelector("strong").textContent = item.label;
  row.querySelector("small").textContent = item.description || item.path || item.command || "";
  row.querySelector("code").textContent = integrationCommand(item);
  row.querySelector(".badge").textContent = item.popular ? "Popular" : item.category || "Custom";
  row.querySelector(".hint").textContent = item.category || item.transport || "";
  return row;
}

function collectToggleItems(listId) {
  return [...$(listId).querySelectorAll(".list-item")].map((row) => {
    const item = JSON.parse(row.dataset.item);
    item.enabled = row.querySelector("input").checked;
    return item;
  });
}

function integrationCommand(item) {
  if (item.transport === "http") return item.url || "";
  const args = Array.isArray(item.args) ? item.args.join(" ") : "";
  return [item.command, args].filter(Boolean).join(" ");
}

function parseArgs(value) {
  return String(value || "")
    .split(" ")
    .map((item) => item.trim())
    .filter(Boolean);
}

function parsePairs(value) {
  const pairs = {};
  for (const chunk of String(value || "").split(",")) {
    const [key, ...rest] = chunk.split("=");
    if (key && rest.length) pairs[key.trim()] = rest.join("=").trim();
  }
  return pairs;
}

function slugify(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 64) || `custom-${Date.now()}`;
}

function applyIntegrationFilters() {
  filterList("mcp-list", $("mcp-filter")?.value || "");
  filterList("skills-list", $("skill-filter")?.value || "");
}

function filterList(listId, query) {
  const needle = String(query || "").toLowerCase().trim();
  for (const row of $(listId).querySelectorAll(".list-item")) {
    row.classList.toggle("hidden", Boolean(needle) && !row.dataset.search.includes(needle));
  }
}

function updateIntegrationPreview() {
  const enabledMcp = collectToggleItems("mcp-list").filter((item) => item.enabled);
  const enabledSkills = collectToggleItems("skills-list").filter((item) => item.enabled);
  $("enabled-mcp-count").textContent = String(enabledMcp.length);
  $("enabled-skill-count").textContent = String(enabledSkills.length);
  $("hero-mcp-count").textContent = String(enabledMcp.length);
  $("hero-skill-count").textContent = String(enabledSkills.length);
  const preview = {
    mcp_servers: Object.fromEntries(
      enabledMcp.map((item) => {
        const value = item.transport === "http"
          ? { transport: "http", url: item.url || "", headers: item.headers || {} }
          : { transport: "stdio", command: item.command || "", args: item.args || [], env: item.env || {} };
        return [item.id, value];
      }),
    ),
    skills: enabledSkills.map((item) => ({
      id: item.id,
      label: item.label,
      path: item.path || "",
      category: item.category || "",
    })),
  };
  $("integration-preview").textContent = JSON.stringify(preview, null, 2);
}

async function loadConfig() {
  const config = await api("/api/config");
  fillForm(config);
  showSetupPanel(false);
}

async function boot() {
  applyTheme();
  applyI18n();
  $("token-input").value = state.setupToken;
  try {
    const health = await api("/api/health");
    setStatus(health.initialized ? "ok" : "", health.initialized ? t("ready") : t("pendingSetup"));
    await loadConfig();
  } catch (error) {
    if (String(error.message).includes("token") || String(error.message).includes("401")) {
      showSetupPanel(true);
      setStatus("", t("tokenRequired"));
      return;
    }
    setStatus("err", t("offline"));
    toast(error.message);
  }
}

function addMessage(role, text) {
  const box = document.createElement("div");
  box.className = `message ${role}`;
  box.textContent = text;
  $("messages").appendChild(box);
  $("messages").scrollTop = $("messages").scrollHeight;
}

function resizeComposer() {
  const input = $("chat-input");
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 180)}px`;
}

for (const item of document.querySelectorAll(".side-item")) {
  item.addEventListener("click", () => showSection(item.dataset.section));
}

for (const item of document.querySelectorAll("[data-jump]")) {
  item.addEventListener("click", () => showSection(item.dataset.jump));
}

$("lang-toggle").addEventListener("click", () => {
  state.lang = state.lang === "zh" ? "en" : "zh";
  localStorage.setItem("hermes-lang", state.lang);
  applyI18n();
  if (state.config) fillForm(state.config);
});

$("theme-toggle").addEventListener("click", () => {
  state.theme = state.theme === "dark" ? "light" : "dark";
  localStorage.setItem("hermes-theme", state.theme);
  applyTheme();
});

$("token-save").addEventListener("click", async () => {
  state.setupToken = $("token-input").value.trim();
  localStorage.setItem("hermes-token", state.setupToken);
  await loadConfig();
  setStatus("ok", t("ready"));
});

$("token-input").addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    $("token-save").click();
  }
});

$("refresh-config").addEventListener("click", async () => {
  await loadConfig();
  toast(t("refresh"));
});

$("model-preset").addEventListener("change", (event) => {
  const option = event.target.selectedOptions[0];
  if (event.target.value) {
    $("model_id").value = event.target.value;
    if (option?.dataset.providerType) $("provider_type").value = option.dataset.providerType;
  }
});

$("config-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const config = await api("/api/config", {
    method: "PUT",
    body: JSON.stringify(readForm()),
  });
  fillForm(config);
  setStatus("ok", t("ready"));
  toast(t("configSaved"));
});

$("provider-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const config = await api("/api/providers/import", {
    method: "POST",
    body: JSON.stringify({
      label: $("provider-label").value,
      provider_type: $("provider-import-type").value,
      model_id: $("provider-model-id").value,
      base_url: $("provider-base-url").value,
      api_key: $("provider-api-key").value,
      aws_region: $("provider-aws-region").value,
      use_now: true,
    }),
  });
  fillForm(config);
  toast(t("configSaved"));
});

$("save-mcp").addEventListener("click", async () => {
  const config = await api("/api/mcp", {
    method: "PUT",
    body: JSON.stringify({ mcp_servers: collectToggleItems("mcp-list") }),
  });
  fillForm(config);
  toast(t("save"));
});

$("custom-mcp-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const label = $("custom-mcp-label").value.trim();
  const transport = $("custom-mcp-transport").value;
  const entry = $("custom-mcp-entry").value.trim();
  if (!label || !entry) return;
  const item = {
    id: `custom-${slugify(label)}`,
    label,
    category: "Custom",
    transport,
    enabled: true,
    popular: false,
    description: transport === "http" ? "Custom hosted MCP endpoint." : "Custom stdio MCP server.",
  };
  if (transport === "http") {
    item.url = entry;
    item.headers = parsePairs($("custom-mcp-env").value);
  } else {
    item.command = entry;
    item.args = parseArgs($("custom-mcp-args").value);
    item.env = parsePairs($("custom-mcp-env").value);
  }
  $("mcp-list").prepend(renderToggleItem(item, "mcp"));
  event.target.reset();
  updateIntegrationPreview();
});

$("save-skills").addEventListener("click", async () => {
  const config = await api("/api/skills", {
    method: "PUT",
    body: JSON.stringify({ skills: collectToggleItems("skills-list") }),
  });
  fillForm(config);
  toast(t("save"));
});

$("custom-skill-form").addEventListener("submit", (event) => {
  event.preventDefault();
  const label = $("custom-skill-label").value.trim();
  const path = $("custom-skill-path").value.trim();
  if (!label || !path) return;
  const item = {
    id: `custom-${slugify(label)}`,
    label,
    path,
    category: $("custom-skill-category").value.trim() || "Custom",
    description: $("custom-skill-description").value.trim() || "Custom skill.",
    enabled: true,
    popular: false,
  };
  $("skills-list").prepend(renderToggleItem(item, "skill"));
  event.target.reset();
  updateIntegrationPreview();
});

$("mcp-filter").addEventListener("input", applyIntegrationFilters);
$("skill-filter").addEventListener("input", applyIntegrationFilters);

$("copy-integration-config").addEventListener("click", async () => {
  if (navigator.clipboard) {
    await navigator.clipboard.writeText($("integration-preview").textContent);
  }
  toast(t("copied"));
});

$("test-bedrock").addEventListener("click", async () => {
  addMessage("assistant", "Testing model...");
  try {
    const result = await api("/api/test", { method: "POST", body: "{}" });
    addMessage("assistant", result.text || "Provider responded.");
  } catch (error) {
    addMessage("error", error.message);
  }
});

$("chat-input").addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
    event.preventDefault();
    $("chat-form").requestSubmit();
  }
});

$("chat-input").addEventListener("input", resizeComposer);

$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (state.sending) return;
  const input = $("chat-input");
  const message = input.value.trim();
  if (!message) return;
  state.sending = true;
  input.value = "";
  resizeComposer();
  addMessage("user", message);
  const sendButton = $("chat-form").querySelector("button[type='submit']");
  sendButton.disabled = true;
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    addMessage("assistant", result.text || "(empty response)");
  } catch (error) {
    addMessage("error", error.message);
  } finally {
    state.sending = false;
    sendButton.disabled = false;
    input.focus();
  }
});

$("clear-chat").addEventListener("click", () => {
  $("messages").innerHTML = "";
});

window.addEventListener("unhandledrejection", (event) => {
  toast(event.reason?.message || String(event.reason));
});

boot();
