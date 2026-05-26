# Hermes Agent on Rocky Linux EC2

Hermes Agent 是一个部署在 Rocky Linux EC2 实例上的轻量级 Web UI 与 Amazon Bedrock 调用桥接服务。它会在实例本地保存运行配置，通过首次启动生成的 setup token 保护初始化入口，并使用 EC2 IAM Role 通过 AWS SDK 调用 Bedrock 托管模型，例如 Amazon Nova 系列模型。

## 架构说明

本项目包含以下内容：

- `hermes_agent/`：Hermes Agent 后端服务和 Web UI 静态页面。
- `packaging/scripts/install.sh`：在已有 Rocky Linux EC2 上安装 Hermes Agent。
- `packaging/systemd/`：Hermes Agent 和首次启动初始化的 systemd 服务。
- `packaging/packer/`：用于制作可复用 Rocky Linux AMI 的 Packer 模板。
- `packaging/terraform/`：基于 AMI 一键启动 EC2、IAM Role、安全组和 user data 的 Terraform 示例。

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

输入 setup token 后，在 Web UI 中配置：

- `AWS Region`：Bedrock 模型所在 Region，例如 `us-east-1`。
- `模型 ID`：例如 `us.amazon.nova-lite-v1:0`。
- `系统提示词`：Hermes Agent 的默认系统提示词。
- `Temperature`、`Top P`、`Max tokens`：模型推理参数。

保存配置后，点击 `测试 Bedrock` 验证模型调用是否成功。

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
