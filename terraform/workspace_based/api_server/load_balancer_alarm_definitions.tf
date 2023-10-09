# Alarm on UnHealthyHostCount (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "unhealthy_host_count" {
  alarm_name                = "${var.name}-unhealthy-host-count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors unhealthy host count"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "UnHealthyHostCount"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Sum"
  dimensions                = {LoadBalancer = aws_alb.this.arn, TargetGroup = aws_lb_target_group.this.arn}
}

# Error rate:
# Alarm on HTTPCode_Target_5XX_Count (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "http_5xx_count" {
  alarm_name                = "${var.name}-http-5xx-count"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors http 5xx count"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "HTTPCode_Target_5XX_Count"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Sum"
  dimensions                = {LoadBalancer = aws_alb.this.arn, TargetGroup = aws_lb_target_group.this.arn}
}

# latency:
# Alarm on TargetResponseTime (namespace: AWS/ApplicationELB)
resource "aws_cloudwatch_metric_alarm" "target_response_time" {
  alarm_name                = "${var.name}-target-response-time"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = 1
  threshold                 = 1
  alarm_description         = "This metric monitors target response time"
  alarm_actions             = [var.pager_duty_sns_topic_arn]
  metric_name               = "TargetResponseTime"
  namespace                 = "AWS/ApplicationELB"
  period                    = 60
  statistic                 = "Average"
  dimensions                = {LoadBalancer = aws_alb.this.arn, TargetGroup = aws_lb_target_group.this.arn}
}
