# Product Listing Draft

## Product Title

Hermes Agent on Rocky Linux

## Short Description

Hermes Agent is a lightweight Web UI and multi-model operations bridge for Amazon Bedrock and OpenAI-compatible providers, packaged as a Rocky Linux AMI for AWS Marketplace.

## Long Description

Hermes Agent helps cloud and AI teams deploy a secure, self-hosted agent console on Amazon EC2. The product provides a web console for configuring Amazon Bedrock models, external model providers, MCP servers, skills, and runtime settings.

The default deployment uses an EC2 instance profile to call Amazon Bedrock, so buyers do not need to enter AWS access keys in the application. First boot generates a unique setup token for each instance, and AWS Systems Manager can be used to retrieve the token without broadly opening SSH.

The included CloudFormation deployment option creates a dedicated VPC, public subnet, security group, IAM role, instance profile, and EC2 instance. Production architectures can extend the deployment with API Gateway, VPC Link, internal Network Load Balancer, private subnet egress through NAT Gateway, CloudWatch, and Secrets Manager.

## Highlights

- Amazon Bedrock Converse API integration through EC2 IAM Role.
- External OpenAI-compatible, Anthropic, and Google Gemini provider configuration.
- MCP and skill configuration hub with runtime manifest preview.
- Setup-token protected Web UI.
- Systems Manager support for operational access and token retrieval.
- Marketplace-ready PRM hooks for EC2 metering, resource tagging, and Bedrock User Agent attribution.

## Categories

- Machine Learning
- Generative AI
- Application Development
- DevOps

## Recommended Instance Type

`t3.small` for evaluation, `t3.medium` or larger for production use.

## Usage Instructions

See `USAGE_INSTRUCTIONS.md`.

## Support

Support should include:

- Product version and AMI ID.
- AWS Region and instance ID.
- `sudo hermes-agent-ctl status` output.
- Relevant `sudo hermes-agent-ctl logs` excerpts.
- Bedrock model ID and Region used for testing.

Do not send setup tokens, API keys, private prompts, customer data, or AWS credentials in support requests.

