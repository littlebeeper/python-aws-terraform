variable "pager_duty_sns_topic_arn" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "egress_security_group_id" {
  type = string
}

variable "internet_gateway_id" {
  type = string
}