provider "aws" {
  region  = "us-west-1"
  profile = "jay"
}

provider "mongodbatlas" {
  public_key  = var.mongodbatlas_public_key
  private_key = var.mongodbatlas_private_key
}

provider "archive" {}

terraform {
  required_version = ">= 1.0"

  backend "s3" {
    bucket  = "mogara-terraform"
    key     = "terraform.tfstate"
    region  = "us-west-1"
    profile = "jay"
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.67.0"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.4.3"
    }
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.6.1"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.3.0"
    }
  }
}
