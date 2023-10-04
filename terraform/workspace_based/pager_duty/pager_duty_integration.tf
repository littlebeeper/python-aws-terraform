data "aws_secretsmanager_secret_version" "pagerduty_integration_key" {
  secret_id = "${terraform.workspace}/pager_duty/integration_key"
}

# (publisher) where alerts will be published
resource "aws_sns_topic" "pagerduty" {
  name = "${terraform.workspace}-notify-pagerduty"
}

# (subscriber) PagerDuty will fire our alerts for us
resource "aws_sns_topic_subscription" "pagerduty_alerts_subscription" {
  topic_arn = aws_sns_topic.pagerduty.arn
  protocol  = "https"
  endpoint  = "https://events.pagerduty.com/integration/${data.aws_secretsmanager_secret_version.pagerduty_integration_key.secret_string}/enqueue"
}
