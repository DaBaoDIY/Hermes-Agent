#!/usr/bin/env bash
set -euo pipefail

REGION="${REGION:-us-east-1}"
SELLER_ACCOUNT_ID="${SELLER_ACCOUNT_ID:-249583190302}"
AMI_ID="${AMI_ID:-ami-09f49fe6148baa5f0}"
VERSION_TITLE="${VERSION_TITLE:-v1.0.0}"
RELEASE_NOTES="${RELEASE_NOTES:-Initial AWS Marketplace release of Hermes Agent on Rocky Linux.}"
ROLE_NAME="${ROLE_NAME:-AwsMarketplaceAmiIngestion}"
ASSET_BUCKET="${ASSET_BUCKET:-hermes-agent-marketplace-assets-${SELLER_ACCOUNT_ID}-${REGION}}"
PRODUCT_TITLE="${PRODUCT_TITLE:-Hermes Agent on Rocky Linux}"
PRODUCT_SKU="${PRODUCT_SKU:-hermes-agent-rocky-${VERSION_TITLE}}"
OFFER_NAME="${OFFER_NAME:-Hermes Agent public offer}"
MARKETPLACE_REGIONS="${MARKETPLACE_REGIONS:-us-east-1}"
MARKETPLACE_INSTANCE_TYPES="${MARKETPLACE_INSTANCE_TYPES:-t3.small,t3.medium,m6i.large}"
RECOMMENDED_INSTANCE_TYPE="${RECOMMENDED_INSTANCE_TYPE:-t3.small}"
MARKETPLACE_OS_NAME="${MARKETPLACE_OS_NAME:-CENTOS}"
MARKETPLACE_OS_VERSION="${MARKETPLACE_OS_VERSION:-Rocky Linux 9 x86_64}"
WORK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TEMPLATE_PATH="${WORK_DIR}/cloudformation/hermes-agent-marketplace.yaml"
ARCHITECTURE_PATH="${WORK_DIR}/assets/hermes-agent-architecture.png"
LOGO_PATH="${WORK_DIR}/assets/hermes-agent-logo.png"
USAGE_PATH="${WORK_DIR}/USAGE_INSTRUCTIONS.md"

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

require_cmd aws
require_cmd python3

echo "==> Checking AWS caller identity"
CALLER_ACCOUNT="$(aws sts get-caller-identity --query Account --output text)"
if [[ "${CALLER_ACCOUNT}" != "${SELLER_ACCOUNT_ID}" ]]; then
  echo "Current AWS account is ${CALLER_ACCOUNT}, expected ${SELLER_ACCOUNT_ID}." >&2
  exit 1
fi

echo "==> Checking AMI ${AMI_ID} in ${REGION}"
aws ec2 describe-images \
  --region "${REGION}" \
  --image-ids "${AMI_ID}" \
  --query 'Images[0].{ImageId:ImageId,Name:Name,Architecture:Architecture,VirtualizationType:VirtualizationType,RootDeviceType:RootDeviceType,State:State,BlockDeviceMappings:BlockDeviceMappings}' \
  --output table

echo "==> Validating CloudFormation template"
aws cloudformation validate-template \
  --region "${REGION}" \
  --template-body "file://${TEMPLATE_PATH}" >/dev/null

echo "==> Ensuring Marketplace AMI ingestion role"
if ! aws iam get-role --role-name "${ROLE_NAME}" >/dev/null 2>&1; then
  TRUST_FILE="$(mktemp)"
  POLICY_FILE="$(mktemp)"
  cat > "${TRUST_FILE}" <<'JSON'
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
JSON
  cat > "${POLICY_FILE}" <<'JSON'
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
JSON
  aws iam create-role \
    --role-name "${ROLE_NAME}" \
    --assume-role-policy-document "file://${TRUST_FILE}" >/dev/null
  aws iam put-role-policy \
    --role-name "${ROLE_NAME}" \
    --policy-name "${ROLE_NAME}-policy" \
    --policy-document "file://${POLICY_FILE}" >/dev/null
  rm -f "${TRUST_FILE}" "${POLICY_FILE}"
fi
ROLE_ARN="$(aws iam get-role --role-name "${ROLE_NAME}" --query 'Role.Arn' --output text)"

echo "==> Ensuring public S3 asset bucket ${ASSET_BUCKET}"
if ! aws s3api head-bucket --bucket "${ASSET_BUCKET}" >/dev/null 2>&1; then
  aws s3api create-bucket --bucket "${ASSET_BUCKET}" --region "${REGION}" >/dev/null
fi
aws s3api put-public-access-block \
  --bucket "${ASSET_BUCKET}" \
  --public-access-block-configuration \
  'BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false' >/dev/null
aws s3api put-bucket-policy \
  --bucket "${ASSET_BUCKET}" \
  --policy "{
    \"Version\": \"2012-10-17\",
    \"Statement\": [{
      \"Sid\": \"PublicReadMarketplaceAssets\",
      \"Effect\": \"Allow\",
      \"Principal\": \"*\",
      \"Action\": \"s3:GetObject\",
      \"Resource\": \"arn:aws:s3:::${ASSET_BUCKET}/*\"
    }]
  }" >/dev/null

echo "==> Uploading Marketplace assets"
aws s3 cp "${TEMPLATE_PATH}" "s3://${ASSET_BUCKET}/cloudformation/hermes-agent-marketplace.yaml" \
  --content-type "text/yaml" >/dev/null
aws s3 cp "${ARCHITECTURE_PATH}" "s3://${ASSET_BUCKET}/assets/hermes-agent-architecture.png" \
  --content-type "image/png" >/dev/null
aws s3 cp "${LOGO_PATH}" "s3://${ASSET_BUCKET}/assets/hermes-agent-logo.png" \
  --content-type "image/png" >/dev/null
aws s3 cp "${USAGE_PATH}" "s3://${ASSET_BUCKET}/docs/USAGE_INSTRUCTIONS.md" \
  --content-type "text/markdown; charset=utf-8" >/dev/null

TEMPLATE_URL="https://${ASSET_BUCKET}.s3.amazonaws.com/cloudformation/hermes-agent-marketplace.yaml"
ARCHITECTURE_URL="https://${ASSET_BUCKET}.s3.amazonaws.com/assets/hermes-agent-architecture.png"
LOGO_URL="https://${ASSET_BUCKET}.s3.amazonaws.com/assets/hermes-agent-logo.png"
USAGE_URL="https://${ASSET_BUCKET}.s3.amazonaws.com/docs/USAGE_INSTRUCTIONS.md"

CHANGE_SET_FILE="$(mktemp)"
python3 - "${CHANGE_SET_FILE}" \
  "${PRODUCT_TITLE}" \
  "${PRODUCT_SKU}" \
  "${OFFER_NAME}" \
  "${VERSION_TITLE}" \
  "${RELEASE_NOTES}" \
  "${MARKETPLACE_REGIONS}" \
  "${MARKETPLACE_INSTANCE_TYPES}" \
  "${RECOMMENDED_INSTANCE_TYPE}" \
  "${MARKETPLACE_OS_NAME}" \
  "${MARKETPLACE_OS_VERSION}" \
  "${TEMPLATE_URL}" \
  "${ARCHITECTURE_URL}" \
  "${LOGO_URL}" \
  "${USAGE_URL}" \
  "${AMI_ID}" \
  "${ROLE_ARN}" <<'PY'
import json
import sys

(
    path,
    product_title,
    product_sku,
    offer_name,
    version_title,
    release_notes,
    marketplace_regions,
    marketplace_instance_types,
    recommended_instance_type,
    marketplace_os_name,
    marketplace_os_version,
    template_url,
    architecture_url,
    logo_url,
    usage_url,
    ami_id,
    role_arn,
) = sys.argv[1:]

regions = [item.strip() for item in marketplace_regions.split(",") if item.strip()]
instance_types = [item.strip() for item in marketplace_instance_types.split(",") if item.strip()]
if not regions:
    raise SystemExit("MARKETPLACE_REGIONS must include at least one region")
if not instance_types:
    raise SystemExit("MARKETPLACE_INSTANCE_TYPES must include at least one instance type")

description = (
    "Hermes Agent is a lightweight Web UI and multi-model operations bridge "
    "for Amazon Bedrock and OpenAI-compatible providers, packaged as a Rocky "
    "Linux AMI for AWS Marketplace."
)

change_set = [
    {
        "ChangeType": "CreateProduct",
        "ChangeName": "CreateHermesProduct",
        "Entity": {
            "Type": "AmiProduct@1.0",
        },
        "DetailsDocument": {
            "ProductTitle": product_title,
        },
    },
    {
        "ChangeType": "CreateOffer",
        "ChangeName": "CreateHermesOffer",
        "Entity": {
            "Type": "Offer@1.0",
        },
        "DetailsDocument": {
            "Name": offer_name,
            "ProductId": "$CreateHermesProduct.Entity.Identifier",
        },
    },
    {
        "ChangeType": "UpdateInformation",
        "ChangeName": "UpdateHermesInformation",
        "Entity": {
            "Type": "AmiProduct@1.0",
            "Identifier": "$CreateHermesProduct.Entity.Identifier",
        },
        "DetailsDocument": {
            "ProductTitle": product_title,
            "ShortDescription": "Self-hosted AI agent console for Amazon Bedrock on Rocky Linux.",
            "LongDescription": description,
            "Sku": product_sku,
            "LogoUrl": logo_url,
            "Highlights": [
                "Amazon Bedrock Converse API integration through EC2 IAM Role.",
                "Setup-token protected Web UI with Systems Manager token retrieval.",
                "MCP and skill configuration hub with AWS Marketplace PRM hooks.",
            ],
            "Categories": ["Application Development", "Operating Systems"],
            "SearchKeywords": ["Amazon Bedrock", "Generative AI", "Agent", "Rocky Linux"],
            "AdditionalResources": [
                {
                    "Text": "Usage instructions",
                    "Url": usage_url,
                }
            ],
            "SupportDescription": "Support includes deployment, startup, configuration, and Amazon Bedrock connectivity troubleshooting. Do not send credentials, setup tokens, API keys, or private prompts in support requests.",
        },
    },
    {
        "ChangeType": "AddRegions",
        "ChangeName": "AddHermesRegions",
        "Entity": {
            "Type": "AmiProduct@1.0",
            "Identifier": "$CreateHermesProduct.Entity.Identifier",
        },
        "DetailsDocument": {
            "Regions": regions,
        },
    },
    {
        "ChangeType": "AddInstanceTypes",
        "ChangeName": "AddHermesInstanceTypes",
        "Entity": {
            "Type": "AmiProduct@1.0",
            "Identifier": "$CreateHermesProduct.Entity.Identifier",
        },
        "DetailsDocument": {
            "InstanceTypes": instance_types,
        },
    },
    {
        "ChangeType": "AddDeliveryOptions",
        "ChangeName": "AddHermesCloudFormationDelivery",
        "Entity": {
            "Type": "AmiProduct@1.0",
            "Identifier": "$CreateHermesProduct.Entity.Identifier",
        },
        "DetailsDocument": {
            "Version": {
                "VersionTitle": version_title,
                "ReleaseNotes": release_notes,
            },
            "DeliveryOptions": [
                {
                    "DeliveryOptionTitle": "CloudFormation deployment",
                    "Details": {
                        "DeploymentTemplateDeliveryOptionDetails": {
                            "ShortDescription": "Deploy Hermes Agent on Rocky Linux with Amazon Bedrock IAM access.",
                            "LongDescription": "This CloudFormation template deploys Hermes Agent on Amazon EC2 with a dedicated VPC, public subnet, security group, IAM role, instance profile, and Systems Manager access.",
                            "UsageInstructions": "After the stack reaches CREATE_COMPLETE, open the WebUrl output and retrieve the setup token with the SetupTokenCommand output.",
                            "RecommendedInstanceType": recommended_instance_type,
                            "ArchitectureDiagram": architecture_url,
                            "Template": template_url,
                            "TemplateSources": [
                                {
                                    "ParameterName": "AmiId",
                                    "AmiSource": {
                                        "AmiId": ami_id,
                                        "AccessRoleArn": role_arn,
                                        "UserName": "rocky",
                                        "OperatingSystemName": marketplace_os_name,
                                        "OperatingSystemVersion": marketplace_os_version,
                                    },
                                }
                            ],
                        }
                    },
                }
            ],
        },
    },
]

with open(path, "w", encoding="utf-8") as handle:
    json.dump(change_set, handle, indent=2)
PY

echo "==> Submitting draft AMI product change set"
aws marketplace-catalog start-change-set \
  --catalog AWSMarketplace \
  --change-set "file://${CHANGE_SET_FILE}" \
  --region "${REGION}" \
  --output json

rm -f "${CHANGE_SET_FILE}"
