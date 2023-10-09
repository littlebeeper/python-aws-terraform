# secrets manager key that contains our PagerDuty integration key
# Steps to setup:
# 1. Create a new service in PagerDuty
# 2. Create a new AWS integration key in PagerDuty
# 3. Add integration to AWS Secrets Manager (name it "${name}/pager_duty/integration_key")
data "aws_secretsmanager_secret_version" "pagerduty_integration_key" {
  secret_id = "${var.name}/pager_duty/integration_key"
}

# (publisher) where alerts will be published
resource "aws_sns_topic" "pagerduty" {
  name = "${var.name}-notify-pagerduty"
}

# (subscriber) PagerDuty will fire our alerts for us
resource "aws_sns_topic_subscription" "pagerduty_alerts_subscription" {
  topic_arn = aws_sns_topic.pagerduty.arn
  protocol  = "https"
  endpoint  = "https://events.pagerduty.com/integration/${data.aws_secretsmanager_secret_version.pagerduty_integration_key.secret_string}/enqueue"
}
