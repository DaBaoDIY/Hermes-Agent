output "instance_id" {
  value = aws_instance.this.id
}

output "public_ip" {
  value = aws_instance.this.public_ip
}

output "web_url" {
  value = "http://${aws_instance.this.public_ip}:8080"
}

output "setup_token_command" {
  value = "aws ssm send-command --region ${var.aws_region} --instance-ids ${aws_instance.this.id} --document-name AWS-RunShellScript --parameters commands='sudo cat /etc/hermes-agent/setup-token'"
}
