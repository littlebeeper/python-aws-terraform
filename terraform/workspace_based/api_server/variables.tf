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

variable "api_url" {
  type = string
}

variable "region" {
  type = string
}

variable name {
    type = string
}

variable env_bucket_name {
    type = string
}

variable cloudwatch_500s_alarm_name {
  type = string
}
