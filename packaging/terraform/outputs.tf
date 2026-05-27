output "instance_id" {
  value = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}

output "web_url" {
  value = var.associate_public_ip_address ? "http://${aws_instance.this.public_ip}:8080" : null
}

output "api_gateway_url" {
  value = var.enable_api_gateway ? aws_apigatewayv2_api.this[0].api_endpoint : null
}

output "nat_gateway_id" {
  value = var.enable_nat_gateway ? aws_nat_gateway.this[0].id : null
}

output "setup_token_command" {
  value = "aws ssm send-command --region ${var.aws_region} --instance-ids ${aws_instance.this.id} --document-name AWS-RunShellScript --parameters commands='sudo cat /etc/hermes-agent/setup-token'"
}
