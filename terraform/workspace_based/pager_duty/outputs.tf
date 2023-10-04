output "service_key" {
  value = local.service_key
}

output "pager_duty_sns_topic_arn" {
  value = aws_sns_topic.pagerduty.arn
}
