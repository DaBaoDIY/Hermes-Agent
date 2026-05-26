const state = {
  token: localStorage.getItem("hermes-token") || "",
  config: null,
};

const $ = (id) => document.getElementById(id);

function headers() {
  const base = { "Content-Type": "application/json" };
  if (state.token) base["X-Hermes-Token"] = state.token;
  return base;
}

function toast(message) {
  const box = $("toast");
  box.textContent = message;
  box.classList.remove("hidden");
  window.clearTimeout(box._timer);
  box._timer = window.setTimeout(() => box.classList.add("hidden"), 3600);
}

function setStatus(kind, text) {
  $("status-dot").className = `dot ${kind || ""}`;
  $("status-text").textContent = text;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { ...headers(), ...(options.headers || {}) },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = payload.error || `HTTP ${response.status}`;
    throw new Error(error);
  }
  return payload;
}

function readForm() {
  return {
    aws_region: $("aws_region").value.trim(),
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
  $("aws_region").value = config.aws_region || "";
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
    option.textContent = item.label;
    preset.appendChild(option);
  }
  const custom = document.createElement("option");
  custom.value = "";
  custom.textContent = "Custom";
  preset.appendChild(custom);
  preset.value = [...preset.options].some((option) => option.value === config.model_id) ? config.model_id : "";
}

async function loadHealth() {
  try {
    const health = await api("/api/health");
    setStatus(health.ok ? "ok" : "err", health.initialized ? "已初始化" : "待配置");
    $("auth-panel").classList.toggle("hidden", !health.auth_required || Boolean(state.token));
    return health;
  } catch (error) {
    setStatus("err", "离线");
    throw error;
  }
}

async function loadConfig() {
  const config = await api("/api/config");
  fillForm(config);
}

function addMessage(role, text) {
  const box = document.createElement("div");
  box.className = `message ${role}`;
  box.textContent = text;
  $("messages").appendChild(box);
  $("messages").scrollTop = $("messages").scrollHeight;
}

async function boot() {
  try {
    await loadHealth();
    if (state.token || $("auth-panel").classList.contains("hidden")) {
      await loadConfig();
    }
  } catch (error) {
    if (String(error.message).includes("token")) {
      $("auth-panel").classList.remove("hidden");
      setStatus("err", "需要令牌");
    } else {
      toast(error.message);
    }
  }
}

$("token-save").addEventListener("click", async () => {
  state.token = $("token-input").value.trim();
  localStorage.setItem("hermes-token", state.token);
  try {
    await loadConfig();
    $("auth-panel").classList.add("hidden");
    toast("已连接");
  } catch (error) {
    toast(error.message);
  }
});

$("refresh-config").addEventListener("click", async () => {
  try {
    await loadConfig();
    toast("配置已刷新");
  } catch (error) {
    toast(error.message);
  }
});

$("model-preset").addEventListener("change", (event) => {
  if (event.target.value) $("model_id").value = event.target.value;
});

$("config-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const config = await api("/api/config", {
      method: "PUT",
      body: JSON.stringify(readForm()),
    });
    fillForm(config);
    setStatus("ok", "已初始化");
    toast("配置已保存");
  } catch (error) {
    toast(error.message);
  }
});

$("test-bedrock").addEventListener("click", async () => {
  addMessage("assistant", "Testing Bedrock...");
  try {
    const result = await api("/api/test", { method: "POST", body: "{}" });
    addMessage("assistant", result.text || "Bedrock responded.");
  } catch (error) {
    addMessage("error", error.message);
  }
});

$("chat-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const input = $("chat-input");
  const message = input.value.trim();
  if (!message) return;
  input.value = "";
  addMessage("user", message);
  try {
    const result = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    addMessage("assistant", result.text || "(empty response)");
  } catch (error) {
    addMessage("error", error.message);
  }
});

$("clear-chat").addEventListener("click", () => {
  $("messages").innerHTML = "";
});

boot();
