# example alarm definition
#resource "aws_cloudwatch_metric_alarm" "lambda_error_rate" {
#  alarm_name                = "${local.scoped_name}-lambda-error-rate"
#  comparison_operator       = "GreaterThanOrEqualToThreshold"
#  evaluation_periods        = 1
#  threshold                 = 2
#  alarm_description         = "This metric monitors lambda error rate"
#  alarm_actions             = [var.pager_duty_sns_topic_arn]
#  metric_name               = "Errors"
#  namespace                 = "AWS/Lambda"
#  period                    = 120
#  statistic                 = "Sum"
#  dimensions                = {FunctionName = aws_lambda_function.lambda_function.function_name}
#}


# unhealth host count
# Alarm on UnHealthyHostCount (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "unhealthy_host_count" {
  alarm_name                = "${local.mapi_scoped_name}-unhealthy-host-count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors unhealthy host count"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "UnHealthyHostCount"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Sum"
  dimensions                = {LoadBalancer = aws_alb.mapi.arn, TargetGroup = aws_lb_target_group.mapi.arn}
}

# Error rate:
# Alarm on HTTPCode_Target_5XX_Count (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "http_5xx_count" {
  alarm_name                = "${local.mapi_scoped_name}-http-5xx-count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors http 5xx count"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "HTTPCode_Target_5XX_Count"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Sum"
  dimensions                = {LoadBalancer = aws_alb.mapi.arn, TargetGroup = aws_lb_target_group.mapi.arn}
}

# latency:
# Alarm on TargetResponseTime (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "target_response_time" {
  alarm_name                = "${local.mapi_scoped_name}-target-response-time"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors target response time"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "TargetResponseTime"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Average"
  dimensions                = {LoadBalancer = aws_alb.mapi.arn, TargetGroup = aws_lb_target_group.mapi.arn}
}
