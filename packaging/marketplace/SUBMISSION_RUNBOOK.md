# AWS Marketplace Submission Runbook

This runbook adapts the provided CloudClaw Marketplace and PRM experience to Hermes Agent.

## 1. Seller and IAM Setup

1. Register or sign in to AWS Marketplace Management Portal.
2. Confirm seller account and Partner Central account association.
3. Create the Marketplace AMI ingestion role in the seller account:

Role name:

```text
AwsMarketplaceAmiIngestion
```

Trust policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "assets.marketplace.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

Permission policy:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:ModifyImageAttribute",
        "ec2:DescribeImages",
        "ec2:ModifySnapshotAttribute",
        "ec2:DescribeSnapshots"
      ],
      "Resource": "*"
    }
  ]
}
```

## 2. Build the AMI

Build in `us-east-1`:

```bash
cd packaging/packer
packer init .
packer build -var aws_region=us-east-1 hermes-agent-rocky.pkr.hcl
```

Before creating or submitting the AMI, verify:

```bash
aws ec2 describe-images \
  --region us-east-1 \
  --image-ids ami-REPLACE \
  --query 'Images[0].{VirtualizationType:VirtualizationType,Architecture:Architecture,RootDeviceType:RootDeviceType,BlockDeviceMappings:BlockDeviceMappings}'
```

## 3. Upload Submission Assets

Create an S3 bucket for public Marketplace assets:

```bash
aws s3 mb s3://REPLACE-hermes-marketplace-assets --region us-east-1
aws s3 cp packaging/marketplace/cloudformation/hermes-agent-marketplace.yaml \
  s3://REPLACE-hermes-marketplace-assets/cloudformation/hermes-agent-marketplace.yaml
aws s3 cp packaging/marketplace/assets/hermes-agent-architecture.png \
  s3://REPLACE-hermes-marketplace-assets/assets/hermes-agent-architecture.png
```

The final architecture diagram should be a PNG exported from the included SVG or an AWS official icon diagram.

## 4. Create Product or Add Delivery Option

Use the AWS Marketplace Management Portal for first-time manual submission, or the Catalog API for automated version updates.

First-time draft product automation:

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

This creates a draft AMI product, draft offer, product information, and CloudFormation delivery option in one Catalog API change set. After it succeeds, complete pricing/legal terms and visibility review in AWS Marketplace Management Portal if any required fields remain.

Catalog API skeleton:

```bash
aws marketplace-catalog start-change-set \
  --catalog AWSMarketplace \
  --change-set file://packaging/marketplace/catalog-api/add-delivery-option.json \
  --region us-east-1
```

Replace all `REPLACE_*` placeholders first.

## 5. Monitor Change Set

```bash
aws marketplace-catalog describe-change-set \
  --catalog AWSMarketplace \
  --change-set-id CHANGESET_ID \
  --region us-east-1 \
  --query '{Status:Status,FailureCode:FailureCode,FailureDescription:FailureDescription,Changes:ChangeSet[].{ChangeName:ChangeName,ChangeType:ChangeType,Entity:Entity,Errors:ErrorDetailList}}'
```

Expected states:

```text
PREPARING -> APPLYING -> SUCCEEDED
```

If it fails, check `ErrorDetailList`. Common fixes:

- `SCAN_ERROR`: rebuild the AMI after cleanup and remove risky UserData commands.
- `DUPLICATE_AMI_ID`: copy the AMI to create a new AMI ID for the new version.
- `VALIDATION_ERROR`: validate CloudFormation syntax and Catalog API fields.

## 6. Limited Listing Validation

From an allowlisted buyer account:

1. Subscribe to the Limited product.
2. Launch the CloudFormation delivery option.
3. Confirm stack `CREATE_COMPLETE`.
4. Open Web UI output.
5. Retrieve setup token through SSM.
6. Test Amazon Bedrock call.
7. Verify EC2 ProductCode.
8. Verify `aws-apn-id` tags.
9. Verify CloudTrail User Agent for Bedrock.

## 7. Public Release

After Limited validation, request Public visibility in the Marketplace Management Portal, or use Catalog API `ReleaseProduct`.

## 8. Version Updates

Marketplace versions require a distinct AMI ID. If only the template changes, copy the AMI:

```bash
aws ec2 copy-image \
  --region us-east-1 \
  --source-region us-east-1 \
  --source-image-id ami-OLD \
  --name "hermes-agent-rocky-v1.0.1-$(date +%Y%m%d)"
```

Then submit a new delivery option version and optionally restrict the previous version.
