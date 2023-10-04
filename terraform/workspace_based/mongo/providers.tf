terraform {
  required_version = ">= 1.0"

  required_providers {
    random = {
      source = "hashicorp/random"
      version = "~> 3.4.3"
    }
    mongodbatlas = {
      source  = "mongodb/mongodbatlas"
      version = "~> 1.6.1"
    }
  }
}
