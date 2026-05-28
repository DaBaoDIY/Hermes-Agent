# Hermes Agent AWS Marketplace 中文上架材料包

本目录是一套中文操作材料，用于将 **Hermes Agent on Rocky Linux** 上架到 AWS Global Marketplace。

---

## 推荐阅读顺序

1. [01-上架操作流程.md](./01-上架操作流程.md)  
   从 Seller 注册、AMI 检查、脚本提交、Limited 测试到 Public 发布的完整流程。

2. [02-上架材料清单.md](./02-上架材料清单.md)  
   汇总 AMI、CloudFormation、架构图、Logo、文案、PRM、脚本等材料。

3. [03-产品文案-中文版.md](./03-产品文案-中文版.md)  
   Marketplace 控制台字段填写参考，内部审批和中文销售沟通可用。

4. [04-客户使用说明.md](./04-客户使用说明.md)  
   客户通过 Marketplace 部署后的使用说明。

5. [05-PRM验证流程.md](./05-PRM验证流程.md)  
   验证 EC2 ProductCode、Resource Tagging、Bedrock User Agent。

6. [06-故障排查.md](./06-故障排查.md)  
   常见上架、部署、Bedrock、PRM 问题排查。

---

## 快速操作命令

项目目录：

```bash
cd "/Users/yebaoxu/Documents/Hermes-Agent on Rocky Linux"
```

本地预检：

```bash
python3 -m pytest
node --check hermes_agent/static/app.js
terraform fmt -check packaging/terraform
bash -n packaging/marketplace/scripts/*.sh
```

首次创建 Draft 产品：

```bash
SELLER_ACCOUNT_ID=249583190302 \
AMI_ID=ami-09f49fe6148baa5f0 \
VERSION_TITLE=v1.0.0 \
MARKETPLACE_REGIONS=us-east-1 \
MARKETPLACE_INSTANCE_TYPES=t3.small,t3.medium,m6i.large \
RECOMMENDED_INSTANCE_TYPE=t3.small \
MARKETPLACE_OS_NAME=CENTOS \
packaging/marketplace/scripts/submit-marketplace-draft-product.sh
```

已有 Product ID 时提交版本：

```bash
SELLER_ACCOUNT_ID=249583190302 \
AMI_ID=ami-09f49fe6148baa5f0 \
PRODUCT_ID=prod-xxxxxxxxxxxx \
VERSION_TITLE=v1.0.0 \
MARKETPLACE_REGIONS=us-east-1 \
MARKETPLACE_INSTANCE_TYPES=t3.small,t3.medium,m6i.large \
RECOMMENDED_INSTANCE_TYPE=t3.small \
MARKETPLACE_OS_NAME=CENTOS \
packaging/marketplace/scripts/submit-marketplace-version.sh
```

查询 Change Set：

```bash
aws marketplace-catalog describe-change-set \
  --catalog AWSMarketplace \
  --change-set-id <CHANGE_SET_ID> \
  --region us-east-1 \
  --query '{Status:Status,FailureCode:FailureCode,FailureDescription:FailureDescription,Changes:ChangeSet[].{ChangeName:ChangeName,ChangeType:ChangeType,Entity:Entity,Errors:ErrorDetailList}}'
```

---

## 当前产品信息

| 项目 | 值 |
|:---|:---|
| Seller AWS Account | `249583190302` |
| AMI ID | `ami-09f49fe6148baa5f0` |
| 源区域 | `us-east-1` |
| 产品名称 | `Hermes Agent on Rocky Linux` |
| 交付方式 | AMI with CloudFormation |
| 默认实例类型 | `t3.small` |
| 默认 OS 用户 | `rocky` |
| Web UI 端口 | `8080` |

---

## 重要提醒

- Marketplace 源 AMI 必须在 `us-east-1`。
- 每次版本更新需要不同 AMI ID。
- 首次发布建议先 Limited 测试，再申请 Public。
- PRM 使用 Product Code，不是 Product ID。
- 正式发布前建议用 AWS 官方 Architecture Icons 精修架构图。
- EULA、Support URL、隐私政策等法律/支持材料需要最终由业务方确认。
