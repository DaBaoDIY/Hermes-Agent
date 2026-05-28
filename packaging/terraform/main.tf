provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_vpc" "selected" {
  id = var.vpc_id
}

locals {
  api_gateway_vpc_link_subnet_ids = length(var.api_gateway_vpc_link_subnet_ids) > 0 ? var.api_gateway_vpc_link_subnet_ids : [var.subnet_id]
  prm_tags                        = var.prm_product_code == "" ? {} : { "aws-apn-id" = "pc:${var.prm_product_code}" }
  common_tags = merge(
    {
      Application = "Hermes Agent"
    },
    local.prm_tags
  )
}

resource "aws_iam_role" "this" {
  name = "${var.name}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(local.common_tags, { Name = "${var.name}-ec2-role" })
}

resource "aws_iam_role_policy" "bedrock" {
  name = "${var.name}-bedrock"
  role = aws_iam_role.this.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "InvokeBedrockModels"
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream",
          "bedrock:Converse",
          "bedrock:ConverseStream",
          "bedrock:ListFoundationModels",
          "bedrock:GetFoundationModel",
          "bedrock:ListInferenceProfiles",
          "bedrock:GetInferenceProfile"
        ]
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.this.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

resource "aws_iam_instance_profile" "this" {
  name = "${var.name}-instance-profile"
  role = aws_iam_role.this.name
}

resource "aws_security_group" "this" {
  name        = "${var.name}-sg"
  description = "Hermes Agent Web UI access"
  vpc_id      = var.vpc_id

  ingress {
    description = "Hermes Web UI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [var.allowed_web_cidr]
  }

  dynamic "ingress" {
    for_each = var.allowed_ssh_cidr == null ? [] : [var.allowed_ssh_cidr]
    content {
      description = "SSH"
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  dynamic "ingress" {
    for_each = var.enable_api_gateway ? [data.aws_vpc.selected.cidr_block] : []
    content {
      description = "Hermes Web UI from API Gateway VPC Link"
      from_port   = 8080
      to_port     = 8080
      protocol    = "tcp"
      cidr_blocks = [ingress.value]
    }
  }

  egress {
    description = "Outbound"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(local.common_tags, { Name = "${var.name}-sg" })
}

resource "aws_security_group" "api_gateway_vpc_link" {
  count       = var.enable_api_gateway ? 1 : 0
  name        = "${var.name}-apigw-vpc-link-sg"
  description = "API Gateway VPC Link egress to Hermes Agent"
  vpc_id      = var.vpc_id

  egress {
    description = "Hermes Agent"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.selected.cidr_block]
  }

  tags = merge(local.common_tags, { Name = "${var.name}-apigw-vpc-link-sg" })
}

resource "aws_instance" "this" {
  ami                         = var.ami_id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  key_name                    = var.key_name
  vpc_security_group_ids      = [aws_security_group.this.id]
  iam_instance_profile        = aws_iam_instance_profile.this.name
  associate_public_ip_address = var.associate_public_ip_address
  user_data_replace_on_change = true

  user_data = templatefile("${path.module}/user_data.tftpl", {
    aws_region       = var.aws_region
    model_id         = var.model_id
    prm_product_code = var.prm_product_code
    system_prompt    = var.system_prompt
  })

  metadata_options {
    http_endpoint = "enabled"
    http_tokens   = "required"
  }

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
  }

  tags = merge(local.common_tags, { Name = var.name })
}

resource "aws_lb" "api" {
  count              = var.enable_api_gateway ? 1 : 0
  name               = "${var.name}-nlb"
  internal           = true
  load_balancer_type = "network"
  subnets            = local.api_gateway_vpc_link_subnet_ids

  tags = merge(local.common_tags, { Name = "${var.name}-nlb" })
}

resource "aws_lb_target_group" "api" {
  count       = var.enable_api_gateway ? 1 : 0
  name        = "${var.name}-tg"
  port        = 8080
  protocol    = "TCP"
  target_type = "instance"
  vpc_id      = var.vpc_id

  health_check {
    enabled  = true
    protocol = "HTTP"
    path     = "/api/health"
  }

  tags = merge(local.common_tags, { Name = "${var.name}-tg" })
}

resource "aws_lb_target_group_attachment" "api" {
  count            = var.enable_api_gateway ? 1 : 0
  target_group_arn = aws_lb_target_group.api[0].arn
  target_id        = aws_instance.this.id
  port             = 8080
}

resource "aws_lb_listener" "api" {
  count             = var.enable_api_gateway ? 1 : 0
  load_balancer_arn = aws_lb.api[0].arn
  port              = 80
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api[0].arn
  }
}

resource "aws_apigatewayv2_vpc_link" "this" {
  count              = var.enable_api_gateway ? 1 : 0
  name               = "${var.name}-vpc-link"
  security_group_ids = [aws_security_group.api_gateway_vpc_link[0].id]
  subnet_ids         = local.api_gateway_vpc_link_subnet_ids
}

resource "aws_apigatewayv2_api" "this" {
  count         = var.enable_api_gateway ? 1 : 0
  name          = "${var.name}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["authorization", "content-type", "x-hermes-token"]
    allow_methods = ["GET", "POST", "PUT", "OPTIONS"]
    allow_origins = var.api_gateway_allowed_origins
  }
}

resource "aws_apigatewayv2_integration" "this" {
  count                  = var.enable_api_gateway ? 1 : 0
  api_id                 = aws_apigatewayv2_api.this[0].id
  connection_id          = aws_apigatewayv2_vpc_link.this[0].id
  connection_type        = "VPC_LINK"
  integration_method     = "ANY"
  integration_type       = "HTTP_PROXY"
  integration_uri        = aws_lb_listener.api[0].arn
  payload_format_version = "1.0"
}

resource "aws_apigatewayv2_route" "default" {
  count     = var.enable_api_gateway ? 1 : 0
  api_id    = aws_apigatewayv2_api.this[0].id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.this[0].id}"
}

resource "aws_apigatewayv2_stage" "default" {
  count       = var.enable_api_gateway ? 1 : 0
  api_id      = aws_apigatewayv2_api.this[0].id
  name        = "$default"
  auto_deploy = true
}

resource "aws_eip" "nat" {
  count  = var.enable_nat_gateway ? 1 : 0
  domain = "vpc"

  tags = merge(local.common_tags, { Name = "${var.name}-nat-eip" })
}

resource "aws_nat_gateway" "this" {
  count         = var.enable_nat_gateway ? 1 : 0
  allocation_id = aws_eip.nat[0].id
  subnet_id     = var.nat_public_subnet_id

  tags = merge(local.common_tags, { Name = "${var.name}-nat" })
}

resource "aws_route" "private_nat" {
  count                  = var.enable_nat_gateway ? 1 : 0
  route_table_id         = var.private_route_table_id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.this[0].id
}
