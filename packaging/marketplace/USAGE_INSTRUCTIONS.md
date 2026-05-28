# Hermes Agent Usage Instructions

## Launch

1. Subscribe to Hermes Agent from AWS Marketplace.
2. Launch the CloudFormation deployment option.
3. Choose an Availability Zone, instance type, and allowed Web UI CIDR.
4. Confirm IAM capabilities and create the stack.
5. Wait for CloudFormation to reach `CREATE_COMPLETE`.

## Access the Console

Open the `WebUrl` stack output:

```text
http://<EC2_PUBLIC_IP>:8080
```

Retrieve the first-boot setup token with the `SetupTokenCommand` stack output. Example:

```bash
aws ssm send-command \
  --region <REGION> \
  --instance-ids <INSTANCE_ID> \
  --document-name AWS-RunShellScript \
  --parameters commands='sudo cat /etc/hermes-agent/setup-token'
```

Enter the setup token in the Web UI to open the Hermes Agent console.

## Configure Amazon Bedrock

Hermes Agent uses the EC2 instance profile to call Amazon Bedrock. No AWS access keys are required in the UI.

1. In the Web UI, open `Runtime Config`.
2. Set the AWS Region where Bedrock model access is enabled.
3. Select or enter a Bedrock model ID or inference profile ID.
4. Save the configuration.
5. Click `Test model`.

If the test fails, verify:

- The target model is enabled in Amazon Bedrock.
- The instance IAM role allows Bedrock runtime invocation.
- The configured Region matches the model Region.
- The instance has outbound HTTPS access.

## Chat

- Press `Enter` to send a message.
- Press `Shift + Enter` to insert a line break.

## Operations

Common commands on the instance:

```bash
sudo hermes-agent-ctl token
sudo hermes-agent-ctl status
sudo hermes-agent-ctl logs
sudo hermes-agent-ctl restart
```

Service units:

```bash
sudo systemctl status hermes-agent
sudo systemctl status hermes-agent-firstboot
sudo journalctl -u hermes-agent -f
```

## Security Notes

- Restrict `AllowedWebCidr` to a trusted office or VPN CIDR.
- Prefer Systems Manager Session Manager instead of opening SSH.
- Rotate external provider API keys outside the AMI lifecycle.
- For production, consider fronting the Web UI with API Gateway or an internal load balancer and private network access.

