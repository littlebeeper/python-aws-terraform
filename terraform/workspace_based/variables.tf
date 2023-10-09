variable "mongodbatlas_public_key" {
  type = string
}

variable "mongodbatlas_private_key" {
  type = string
}

variable "region" {
  type = string
}

variable "api_url" {
  type = map(string)
  default = {
    staging = "api.staging.jaygokhale.com"
  }
}

variable "frontend_url" {
    type = map(string)
    default = {
      staging = "dashboard.staging.jaygokhale.com"
    }
}
