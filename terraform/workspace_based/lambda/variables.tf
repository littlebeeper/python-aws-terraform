variable "egress_security_group_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "pager_duty_sns_topic_arn" {
  type = string
}