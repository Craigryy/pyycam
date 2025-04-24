terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.23.0"
    }
  }

  backend "s3" {
    bucket         = "devops-pycam-app-state"
    key            = "tf-state-setup"
    region         = "eu-north-1"
    encrypt        = true
    dynamodb_table = "devops-pycam-app-tf-lock"
  }
}

provider "aws" {
  region = "eu-north-1"

  default_tags {
    tags = {
      Environment = terraform.workspace
      Project     = var.project
      Contact     = var.contact
      ManageBy    = "Terraform/setup"
    }
  }
}

locals {
  prefix = "${var.prefix}-${terraform.workspace}"
}

data "aws_region" "current" {}
