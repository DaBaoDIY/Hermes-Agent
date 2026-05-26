variable "aws_region" {
  type        = string
  description = "AWS Region for the EC2 instance and Bedrock runtime."
  default     = "us-east-1"
}

variable "name" {
  type        = string
  description = "Name prefix for created AWS resources."
  default     = "hermes-agent"
}

variable "ami_id" {
  type        = string
  description = "Hermes Agent Rocky Linux AMI ID built by Packer."
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type."
  default     = "t3.small"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID."
}

variable "subnet_id" {
  type        = string
  description = "Public or private subnet ID for the EC2 instance."
}

variable "key_name" {
  type        = string
  description = "Optional EC2 key pair name."
  default     = null
}

variable "allowed_web_cidr" {
  type        = string
  description = "CIDR allowed to access the Hermes Web UI on port 8080."
}

variable "allowed_ssh_cidr" {
  type        = string
  description = "CIDR allowed to SSH. Leave null to disable SSH ingress."
  default     = null
}

variable "model_id" {
  type        = string
  description = "Default Bedrock model or inference profile ID."
  default     = "us.amazon.nova-lite-v1:0"
}

variable "system_prompt" {
  type        = string
  description = "Default system prompt for Hermes Agent."
  default     = "You are Hermes Agent, a helpful AI operations assistant."
}
