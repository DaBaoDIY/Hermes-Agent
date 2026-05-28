# Marketplace AMI Precheck

Use this checklist before submitting Hermes Agent to AWS Marketplace.

## AMI

- [ ] Source AMI is in `us-east-1`.
- [ ] AMI is HVM, x86_64, EBS-backed.
- [ ] Root EBS snapshot is not encrypted.
- [ ] AMI name includes product, version, OS, architecture, and build date.
- [ ] No AWS access keys, API keys, setup tokens, SSH authorized keys, or private data are present.
- [ ] `/etc/hermes-agent/setup-token` has been removed before image capture.
- [ ] `/etc/hermes-agent/config.json` has been removed or reset to a non-sensitive default.
- [ ] `/etc/hermes-agent/aws-sdk.env` has been removed unless the AMI is a post-listing product-code build.
- [ ] Logs, shell histories, package caches, and temporary files have been cleaned.
- [ ] SSH root login is disabled by the base image or hardening policy.
- [ ] `cloud-init clean --logs` has been executed.
- [ ] First boot creates a fresh setup token for every buyer instance.

## First Boot

- [ ] No `curl` is used in UserData or firstboot scripts.
- [ ] IMDSv2 token and region discovery use `wget`.
- [ ] `hermes-agent-firstboot.service` starts successfully.
- [ ] `hermes-agent.service` starts successfully.
- [ ] `/api/health` returns healthy.
- [ ] Setup token can be retrieved through SSM.

## AWS Access

- [ ] EC2 instance role includes Bedrock runtime invoke permissions.
- [ ] Bedrock target model access is enabled in the buyer region.
- [ ] Systems Manager managed policy is attached.
- [ ] Security group exposes `TCP 8080` only to the intended CIDR.
- [ ] SSH ingress is disabled unless explicitly requested.

## CloudFormation

- [ ] Template parameter `AmiId` is present and type `AWS::EC2::Image::Id`.
- [ ] Marketplace submission maps `TemplateSources.ParameterName` to `AmiId`.
- [ ] Template deploys IAM role, instance profile, security group, EC2 instance, and web access.
- [ ] Product code parameter is available for PRM after Marketplace assigns it.
- [ ] Resources that support tags include `aws-apn-id=pc:<product-code>` when product code is set.

## Marketplace Assets

- [ ] Product logo is PNG, 1:1 or 2:1, 120-640 px.
- [ ] Architecture diagram final PNG is 1100 x 700 px and uses current AWS icons.
- [ ] EULA is ready as a PDF or public URL.
- [ ] Usage instructions are concise and customer-facing.
- [ ] Support contact, response SLA, and troubleshooting scope are documented.

