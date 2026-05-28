packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = ">= 1.3.0"
    }
  }
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "instance_type" {
  type    = string
  default = "t3.small"
}

variable "ami_name_prefix" {
  type    = string
  default = "hermes-agent-rocky"
}

variable "rocky_ami_owner" {
  type    = string
  default = "792107900819"
}

variable "rocky_ami_name" {
  type    = string
  default = "Rocky-9-EC2-Base-9.*.x86_64-*"
}

locals {
  timestamp = regex_replace(timestamp(), "[- TZ:]", "")
}

source "amazon-ebs" "rocky" {
  region        = var.aws_region
  instance_type = var.instance_type
  ssh_username  = "rocky"
  ami_name      = "${var.ami_name_prefix}-${local.timestamp}"
  imds_support  = "v2.0"

  source_ami_filter {
    filters = {
      name                = var.rocky_ami_name
      root-device-type    = "ebs"
      virtualization-type = "hvm"
      architecture        = "x86_64"
    }
    owners      = [var.rocky_ami_owner]
    most_recent = true
  }

  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 20
    volume_type           = "gp3"
    encrypted             = false
    delete_on_termination = true
  }

  tags = {
    Name        = "${var.ami_name_prefix}-${local.timestamp}"
    Application = "Hermes Agent"
    OS          = "Rocky Linux 9"
  }
}

build {
  name    = "hermes-agent-rocky"
  sources = ["source.amazon-ebs.rocky"]

  provisioner "file" {
    source      = "../../"
    destination = "/tmp/hermes-agent"
  }

  provisioner "shell" {
    inline = [
      "sudo bash /tmp/hermes-agent/packaging/scripts/install.sh /tmp/hermes-agent",
      "sudo systemctl enable hermes-agent-firstboot.service",
      "sudo bash /tmp/hermes-agent/packaging/marketplace/scripts/ami-cleanup.sh",
      "sudo rm -rf /tmp/hermes-agent"
    ]
  }
}
