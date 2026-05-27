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

variable "associate_public_ip_address" {
  type        = bool
  description = "Whether to associate a public IPv4 address with the Hermes EC2 instance."
  default     = true
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

variable "enable_api_gateway" {
  type        = bool
  description = "Create an optional Amazon API Gateway HTTP API through a VPC Link and internal Network Load Balancer."
  default     = false
}

variable "api_gateway_vpc_link_subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for the API Gateway VPC Link and internal Network Load Balancer. Defaults to subnet_id when empty."
  default     = []
}

variable "api_gateway_allowed_origins" {
  type        = list(string)
  description = "CORS allowed origins for the optional API Gateway HTTP API."
  default     = ["*"]
}

variable "enable_nat_gateway" {
  type        = bool
  description = "Create an optional NAT Gateway and default private route for private-subnet egress."
  default     = false
}

variable "nat_public_subnet_id" {
  type        = string
  description = "Public subnet ID for the optional NAT Gateway. Required when enable_nat_gateway is true."
  default     = null
}

variable "private_route_table_id" {
  type        = string
  description = "Private route table ID that should receive the NAT default route. Required when enable_nat_gateway is true."
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
