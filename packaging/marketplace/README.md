# Hermes Agent AWS Marketplace Package

This directory contains the submission materials for publishing Hermes Agent as an AWS Marketplace AMI with CloudFormation delivery option.

## Delivery Model

- Product type: AMI with CloudFormation.
- Pricing model: Free software, buyer pays AWS infrastructure costs.
- Source AMI region: `us-east-1`.
- Runtime OS: Rocky Linux 9, HVM, x86_64, EBS-backed.
- Default AWS services: Amazon EC2, IAM, Amazon Bedrock, Systems Manager, VPC, Security Group.
- Optional production services: Amazon API Gateway, internal Network Load Balancer, NAT Gateway, CloudWatch, Secrets Manager.

## Directory

```text
packaging/marketplace/
├── PRECHECK.md
├── PRODUCT_LISTING.md
├── PRM_GUIDE.md
├── USAGE_INSTRUCTIONS.md
├── assets/
│   ├── hermes-agent-architecture.mmd
│   └── hermes-agent-architecture.svg
├── catalog-api/
│   └── add-delivery-option.json
├── cloudformation/
│   └── hermes-agent-marketplace.yaml
└── scripts/
    └── ami-cleanup.sh
```

## Recommended Publishing Flow

1. Build and validate the Rocky Linux AMI in `us-east-1`.
2. Run the cleanup script before AMI capture or through the Packer template.
3. Create the AMI with an unencrypted EBS snapshot.
4. Upload the CloudFormation template and architecture diagram to a public HTTPS location such as S3.
5. Create or update the AMI product in AWS Marketplace Management Portal or Catalog API.
6. Use `AmiId` as the Marketplace-managed CloudFormation AMI parameter.
7. After AWS Marketplace assigns a product code, update `ProductCode` in the CloudFormation delivery template and verify PRM.
8. Test the Limited listing from an allowlisted buyer account before requesting Public visibility.

## Important Marketplace Notes

- Avoid `curl` in first-boot scripts and CloudFormation user data. This package uses `wget` and Python standard libraries.
- Remove setup tokens, logs, SSH authorized keys, and shell histories before AMI capture.
- Do not bake AWS credentials, external model API keys, or test tokens into the AMI.
- For every new Marketplace version, use a distinct AMI ID, even when the image content is unchanged.
- Use official AWS architecture icons when creating the final PNG architecture diagram for submission. The included SVG is a working draft.

