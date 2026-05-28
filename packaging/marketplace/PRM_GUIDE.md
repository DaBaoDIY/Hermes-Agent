# Hermes Agent PRM Guide

Hermes Agent should use all relevant AWS Partner Revenue Measurement methods for an AMI with CloudFormation Marketplace product.

## Method 1: Marketplace Metering

Coverage:

- Amazon EC2 usage launched through AWS Marketplace subscription flow.

Implementation:

- No application code required.
- Marketplace attaches the product code to EC2 instances launched through the listing.

Validation:

```bash
aws ec2 describe-instances \
  --instance-ids <INSTANCE_ID> \
  --query 'Reservations[0].Instances[0].ProductCodes'
```

## Method 2: Resource Tagging

Coverage:

- EC2
- EBS
- VPC
- Subnets
- Security groups
- NAT Gateway and EIP when enabled
- Load balancer and target group when enabled

Tag format:

```text
Key: aws-apn-id
Value: pc:<MARKETPLACE_PRODUCT_CODE>
```

CloudFormation:

- Set the `ProductCode` parameter after Marketplace assigns the product code.
- The template conditionally adds `aws-apn-id=pc:<ProductCode>` to supported resources.

Terraform:

- Set `-var prm_product_code=<MARKETPLACE_PRODUCT_CODE>`.
- The module adds `aws-apn-id=pc:<product-code>` through `local.prm_tags`.

Validation:

```bash
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=aws-apn-id,Values=pc:<MARKETPLACE_PRODUCT_CODE>
```

## Method 3: User Agent String

Coverage:

- Amazon Bedrock Converse and model runtime calls from Hermes Agent.

Format:

```text
APN_1.1/pc_<MARKETPLACE_PRODUCT_CODE>$
```

Implementation:

- CloudFormation and Terraform write `/etc/hermes-agent/aws-sdk.env` when a product code is provided.
- `hermes-agent.service` loads that file through `EnvironmentFile=-/etc/hermes-agent/aws-sdk.env`.
- `hermes_agent/bedrock.py` passes the app ID into botocore config when supported, and falls back to `user_agent_extra` for older botocore versions.

Validation:

1. Trigger a Bedrock test call from the Web UI.
2. Wait 5-15 minutes for CloudTrail.
3. Look up a Bedrock event:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=EventName,AttributeValue=Converse \
  --max-results 10
```

Confirm the event user agent includes the `APN_1.1` product code marker.

## Timing

Attributed Revenue Dashboard data is delayed. Use CloudTrail and resource tags for immediate implementation validation, then review Partner Central after the relevant billing data becomes available.

