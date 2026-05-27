# Hermes Agent on Rocky Linux EC2

Hermes Agent 是一个部署在 Rocky Linux EC2 实例上的轻量级 Web UI 与多模型调用桥接服务。它会在实例本地保存运行配置，通过首次启动生成的 setup token 保护初始化入口，并支持通过 EC2 IAM Role 调用 Amazon Bedrock，也支持导入外部大模型服务的 API key。

## 架构说明

本项目包含以下内容：

- `hermes_agent/`：Hermes Agent 后端服务和 Web UI 静态页面。
- `hermes_agent/providers.py`：Bedrock、OpenAI-compatible、Anthropic、Google Gemini 等模型连接器。
- `packaging/scripts/install.sh`：在已有 Rocky Linux EC2 上安装 Hermes Agent。
- `packaging/systemd/`：Hermes Agent 和首次启动初始化的 systemd 服务。
- `packaging/packer/`：用于制作可复用 Rocky Linux AMI 的 Packer 模板。
- `packaging/terraform/`：基于 AMI 一键启动 EC2、IAM Role、安全组和 user data 的 Terraform 示例。

Web UI 使用 VSTECS 红蓝品牌色与液态玻璃风格，左上角显示 VSTECS 文字品牌标识，并包含深浅色切换、中英文切换、模型接入、MCP/Skills 能力中心和配置预览。

当前推荐的 AWS 落地架构：

- 计算层：Amazon EC2 运行 Rocky Linux、systemd 与 Hermes Agent Web UI。
- AI 模型层：Amazon Bedrock 作为默认模型运行时，通过 Converse API 调用 Nova、Claude、DeepSeek、Kimi 等模型或 inference profile。
- 身份权限层：EC2 Instance Profile + IAM 最小权限策略，默认不在 Web UI 中录入 AWS AK/SK。
- 网络层：Security Group 控制 `8080` 和可选 `22` 入站；生产私有子网可通过 NAT Gateway 访问 Bedrock、公网模型 API 和远程 MCP endpoint。
- 托管入口层：可选 Amazon API Gateway HTTP API + VPC Link + 内部 Network Load Balancer，统一暴露 HTTPS 入口并保留 setup token 认证。
- 运维层：默认绑定 AWS Systems Manager Managed Instance Core，支持通过 SSM 获取 setup token、进入 Session Manager；后续可接入 CloudWatch Logs/Alarms。
- 密钥层：外部模型 API key 当前保存在本机配置文件并脱敏展示；生产环境建议迁移到 AWS Secrets Manager。

## 在已有 Rocky Linux EC2 上安装

如果你已经启动了一台 Rocky Linux EC2 实例，请使用本章节。

### 1. 准备 IAM Role

EC2 实例需要绑定一个可以调用 Amazon Bedrock 的 IAM Role。最小权限示例如下：

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream",
        "bedrock:Converse",
        "bedrock:ConverseStream",
        "bedrock:ListFoundationModels",
        "bedrock:GetFoundationModel",
        "bedrock:ListInferenceProfiles",
        "bedrock:GetInferenceProfile"
      ],
      "Resource": "*"
    }
  ]
}
```

同时需要在 Amazon Bedrock 控制台中，为同一个 Region 开通目标模型访问权限。

### 2. 放通安全组

在 EC2 安全组中放通以下入站规则：

- Web UI：`TCP 8080`，来源建议只填写你的办公网或本机公网 IP。
- SSH：`TCP 22`，仅在需要远程登录时开放。

如果不想把 `8080` 暴露到公网，可以跳过 Web UI 入站规则，改用后面的 SSH 隧道方式访问。

### 3. 上传项目文件

在本机项目目录执行：

```bash
cd "/Users/yebaoxu/Documents/Hermes-Agent on Rocky Linux"
rsync -av --exclude .git ./ rocky@<EC2_PUBLIC_IP>:/tmp/hermes-agent/
```

如果实例使用 pem 私钥登录：

```bash
rsync -av -e "ssh -i /path/to/key.pem" --exclude .git ./ rocky@<EC2_PUBLIC_IP>:/tmp/hermes-agent/
```

如果你的 Rocky Linux 镜像默认用户不是 `rocky`，请把命令中的 `rocky` 替换成实际用户名。

### 4. 安装并启动 Hermes Agent

SSH 登录实例：

```bash
ssh rocky@<EC2_PUBLIC_IP>
```

如果使用 pem 私钥：

```bash
ssh -i /path/to/key.pem rocky@<EC2_PUBLIC_IP>
```

执行安装：

```bash
sudo bash /tmp/hermes-agent/packaging/scripts/install.sh /tmp/hermes-agent
sudo systemctl enable --now hermes-agent-firstboot.service
```

首次启动初始化会完成以下工作：

- 创建 `/etc/hermes-agent/config.json` 默认配置。
- 生成 `/etc/hermes-agent/setup-token` 初始化令牌。
- 自动探测当前 EC2 所在 AWS Region。
- 启动 `hermes-agent.service`。

### 5. 获取 setup token

```bash
sudo hermes-agent-ctl token
sudo hermes-agent-ctl status
```

### 6. 访问 Web UI

浏览器打开：

```text
http://<EC2_PUBLIC_IP>:8080
```

首次进入 Web UI 后，输入 setup token 即可进入控制台。Web UI 不再提供用户登录页。

进入控制台后可配置：

- `AWS Region`：Bedrock 模型所在 Region，例如 `us-east-1`。
- `模型 ID`：例如 `us.amazon.nova-lite-v1:0`。
- `提供商类型`：Amazon Bedrock、OpenAI Compatible、Anthropic API、Google Gemini API。
- `Base URL`：外部 OpenAI-compatible API 的服务地址。
- `API Key`：外部模型服务密钥，保存后 API 返回会脱敏显示。
- `系统提示词`：Hermes Agent 的默认系统提示词。
- `Temperature`、`Top P`、`Max tokens`：模型推理参数。

保存配置后，点击 `测试模型` 验证模型调用是否成功。

聊天输入框支持按 `Enter` 直接发送消息，使用 `Shift + Enter` 输入换行。

## 模型接入能力

当前 Web UI 支持以下接入方式：

- `Amazon Bedrock`：使用 EC2 IAM Role，无需在 Web UI 中录入 AWS AK/SK。
- `OpenAI Compatible`：支持 OpenAI、OpenRouter、DeepSeek、Kimi、Together、vLLM、LM Studio 等兼容 `/v1/chat/completions` 的 API。
- `Anthropic API`：支持 Anthropic Messages API。
- `Google Gemini API`：支持 Gemini `generateContent` API。

Bedrock 预置了 Nova、Claude、DeepSeek、Kimi、Gemma、OpenAI GPT OSS 等常用模型入口。不同 Region 的 Bedrock 模型 ID 和 inference profile ID 可能会变化，生产环境请以 Bedrock 控制台展示为准，也可以在 Web UI 中手动填写模型 ID。

## MCP 与 Skills

Web UI 已预置常用 MCP 和 skills 开关：

- MCP：Filesystem、GitHub、PostgreSQL、Browser Automation、Remote HTTP MCP。
- Skills：Native MCP、Systematic Debugging、Test Driven Development、Code Review、DSPy、Hugging Face Hub。

MCP/Skills 页面提供“预置能力库 + 自定义接入 + 启用清单 + 配置预览”：

- 预置 MCP：Filesystem、GitHub、Git、Fetch、Memory、Sequential Thinking、Time、PostgreSQL、SQLite、Brave Search、Playwright Browser、Puppeteer、Slack、Google Drive、AWS Docs、Remote HTTP MCP。
- 自定义 MCP：支持 `stdio` 命令型 MCP，也支持远程 `http` MCP endpoint；可填写 args、env 或 headers。
- 预置 Skills：Native MCP、Systematic Debugging、TDD、Code Review、Frontend UX、AWS Bedrock、Terraform IaC、Docker/Kubernetes、RAG、vLLM、DSPy、Hugging Face Hub、Documents、Spreadsheets、Presentations。
- 自定义 Skill：可填写 label、path、category 和 description。
- 配置预览：实时生成启用后的 `mcp_servers` 和 skills manifest，便于后续接入 Hermes Agent runtime。

当前版本会保存 MCP/skills 配置，并生成 runtime 配置预览；下一阶段可以继续实现 MCP 子进程托管、OAuth、工具过滤和 skill 文件同步。

## 使用 SSH 隧道访问 Web UI

如果没有开放安全组 `8080`，可以在本机执行：

```bash
ssh -L 8080:127.0.0.1:8080 rocky@<EC2_PUBLIC_IP>
```

使用 pem 私钥：

```bash
ssh -i /path/to/key.pem -L 8080:127.0.0.1:8080 rocky@<EC2_PUBLIC_IP>
```

然后在本机浏览器打开：

```text
http://127.0.0.1:8080
```

## 常用运维命令

```bash
sudo hermes-agent-ctl token
sudo hermes-agent-ctl config
sudo hermes-agent-ctl logs
sudo hermes-agent-ctl restart
```

也可以直接使用 systemd：

```bash
sudo systemctl status hermes-agent
sudo systemctl restart hermes-agent
sudo journalctl -u hermes-agent -f
```

配置文件位置：

```text
/etc/hermes-agent/config.json
```

setup token 位置：

```text
/etc/hermes-agent/setup-token
```

## 制作可复用 AMI

当你确认在单台 EC2 上安装流程正常后，可以使用 Packer 制作可复用的 Rocky Linux AMI：

```bash
cd packaging/packer
packer init .
packer build -var aws_region=us-east-1 hermes-agent-rocky.pkr.hcl
```

生成 AMI 后，可以使用 `packaging/terraform` 中的 Terraform 示例一键创建 EC2、IAM Role、安全组和启动配置。

## Terraform 部署示例

进入 Terraform 目录：

```bash
cd packaging/terraform
terraform init
terraform apply \
  -var aws_region=us-east-1 \
  -var ami_id=ami-xxxxxxxxxxxxxxxxx \
  -var vpc_id=vpc-xxxxxxxx \
  -var subnet_id=subnet-xxxxxxxx \
  -var allowed_web_cidr=<YOUR_PUBLIC_IP>/32
```

部署完成后，Terraform 会输出 Web UI 地址和获取 setup token 的 SSM 命令。

### 可选：通过 API Gateway 暴露托管入口

如果希望在生产环境使用托管 HTTP API 作为入口，可启用 API Gateway。Terraform 会创建：

- Amazon API Gateway HTTP API。
- API Gateway VPC Link。
- 内部 Network Load Balancer。
- 指向 EC2 `8080` 的 Target Group。
- 允许 VPC 内 NLB 路径访问 Hermes Agent 的安全组规则。

示例：

```bash
terraform apply \
  -var aws_region=us-east-1 \
  -var ami_id=ami-xxxxxxxxxxxxxxxxx \
  -var vpc_id=vpc-xxxxxxxx \
  -var subnet_id=subnet-xxxxxxxx \
  -var allowed_web_cidr=<YOUR_PUBLIC_IP>/32 \
  -var enable_api_gateway=true \
  -var 'api_gateway_vpc_link_subnet_ids=["subnet-private-a","subnet-private-b"]'
```

部署完成后查看 `api_gateway_url` 输出。setup token 仍然通过 `X-Hermes-Token` 或 `Authorization: Bearer <token>` 传递。

### 可选：私有子网 + NAT Gateway 出网

当 EC2 放在私有子网时，可以关闭公网 IP，并通过 NAT Gateway 提供出站访问：

```bash
terraform apply \
  -var aws_region=us-east-1 \
  -var ami_id=ami-xxxxxxxxxxxxxxxxx \
  -var vpc_id=vpc-xxxxxxxx \
  -var subnet_id=subnet-private-a \
  -var allowed_web_cidr=<YOUR_PUBLIC_IP>/32 \
  -var associate_public_ip_address=false \
  -var enable_nat_gateway=true \
  -var nat_public_subnet_id=subnet-public-a \
  -var private_route_table_id=rtb-private
```

这个模式适合配合 API Gateway、SSM Session Manager、VPC Endpoint 或堡垒机使用。若已经由平台团队统一提供 NAT Gateway，只需要把私有路由表指向现有 NAT，本示例的 `enable_nat_gateway` 可以保持 `false`。

## 常见问题

### Web UI 无法访问

检查安全组是否放通 `TCP 8080`，并确认服务正在运行：

```bash
sudo systemctl status hermes-agent
sudo ss -lntp | grep 8080
```

### Bedrock 测试失败

依次检查：

- EC2 是否绑定了正确 IAM Role。
- IAM Role 是否包含 Bedrock 调用权限。
- Bedrock 控制台是否已开通目标模型访问权限。
- Web UI 中的 AWS Region 是否与模型开通 Region 一致。
- 模型 ID 是否正确，例如 `us.amazon.nova-lite-v1:0`。

查看日志：

```bash
sudo hermes-agent-ctl logs
```

### 忘记 setup token

在 EC2 上执行：

```bash
sudo hermes-agent-ctl token
```
