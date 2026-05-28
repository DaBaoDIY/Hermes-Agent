# Hermes Agent PRM 验证流程

PRM 即 AWS Partner Revenue Measurement，用于将客户使用 Hermes Agent 带来的 AWS 消费归因到 Marketplace 产品。

Hermes Agent 建议使用三种方式：

| 方法 | 覆盖服务 | 是否自动 |
|:---|:---|:---|
| Marketplace Metering | EC2 | Marketplace 订阅部署自动 |
| Resource Tagging | VPC、EC2、EBS、Security Group、NAT、NLB 等 | CloudFormation / Terraform 自动打标签 |
| User Agent String | Amazon Bedrock | Hermes Agent systemd 环境变量 + boto3 config |

---

## 1. 获取 Product Code

产品通过 Marketplace 创建后，在 Marketplace Management Portal 的 Product Summary 中找到：

```text
Product Code
```

示例格式：

```text
49kmrspbt15fr9of1bvxrsq4y
```

不要使用 Product ID，例如 `prod-xxxx`。PRM 使用的是 Product Code。

---

## 2. Marketplace Metering 验证

通过 Marketplace 订阅流程启动 EC2 后，实例应自动带 ProductCode。

```bash
aws ec2 describe-instances \
  --instance-ids <INSTANCE_ID> \
  --query 'Reservations[0].Instances[0].ProductCodes' \
  --output json
```

预期包含：

```json
[
  {
    "ProductCodeId": "<PRODUCT_CODE>",
    "ProductCodeType": "marketplace"
  }
]
```

注意：

- 只有通过 Marketplace 订阅流程启动的实例才会有 ProductCode。
- 直接用 AMI ID 启动通常不会有 Marketplace Metering 归因。

---

## 3. Resource Tagging 验证

CloudFormation 模板支持 `ProductCode` 参数。填写后，会对支持标签的资源添加：

```text
Key: aws-apn-id
Value: pc:<PRODUCT_CODE>
```

验证：

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=aws-apn-id,Values=pc:<PRODUCT_CODE> \
  --output table
```

应看到 EC2、VPC、Subnet、Security Group、NAT、NLB 等资源。

---

## 4. Bedrock User Agent 验证

CloudFormation 或 Terraform 会生成：

```text
/etc/hermes-agent/aws-sdk.env
```

内容：

```text
AWS_SDK_UA_APP_ID=APN_1.1/pc_<PRODUCT_CODE>$
```

检查：

```bash
sudo cat /etc/hermes-agent/aws-sdk.env
sudo systemctl show hermes-agent --property=Environment
```

触发 Bedrock 调用：

1. 登录 Hermes Agent Web UI。
2. 打开 `对话`。
3. 点击 `测试模型` 或发送一条消息。

等待 5-15 分钟后查 CloudTrail：

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Converse \
  --max-results 10 \
  --output json
```

检查事件中的 `userAgent`，应包含：

```text
APN_1.1
pc_<PRODUCT_CODE>
```

---

## 5. Partner Central Dashboard

Attributed Revenue Dashboard 路径：

```text
Partner Central -> Partner Insights -> Dashboards -> Attributed Revenue
```

注意：

- Dashboard 数据不是实时的。
- 通常需要月末后再等待一段时间才可见。
- 立即验证应以 EC2 ProductCode、Resource Tagging 和 CloudTrail User Agent 为准。

---

## 6. 验证记录模板

| 项目 | 结果 |
|:---|:---|
| 测试账号 |  |
| Region |  |
| Stack 名称 |  |
| Instance ID |  |
| Product ID |  |
| Product Code |  |
| EC2 ProductCode 是否存在 | 是/否 |
| `aws-apn-id` 标签数量 |  |
| Bedrock CloudTrail User Agent |  |
| Web UI 测试 | 通过/失败 |
| Bedrock 模型测试 | 通过/失败 |

