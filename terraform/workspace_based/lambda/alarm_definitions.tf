# lambda alert definition on error rate
resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
  alarm_name                = "${local.scoped_name}-lambda-error-rate"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 2
  alarm_description         = "This metric monitors lambda error rate"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "Errors"
  namespace                 = "AWS/Lambda"
  period                    = 120
  statistic                 = "Sum"
  dimensions                = {FunctionName = aws_lambda_function.lambda_function.function_name}
}
