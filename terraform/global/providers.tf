provider "aws" {
  region  = "us-west-1"
  profile = "jay"
}

terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket  = "srv-terraform"
    key     = "terraform_global.tfstate"
    region  = "us-west-1"
    profile = "jay"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67.0"
    }
  }
}
