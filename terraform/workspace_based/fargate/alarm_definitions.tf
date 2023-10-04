resource "aws_cloudwatch_metric_alarm" "cpu_utilization" {
  alarm_name                = "${local.mapi_scoped_name}-cpu-utilization-too-high"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  threshold                 = "80"
  alarm_description         = "This metric monitors fargate instance cpu utilization"
  alarm_actions             = [var.pager_duty_sns_topic_arn]

  metric_query {
    id = "utilizedPercent"
    expression = "cpu_used * 100/cpu_total"
    label = "CPU Utilization percentage"
    return_data = true
  }

  metric_query {
    id = "cpu_used"
    metric {
      metric_name = "CpuUtilized"
      namespace   = "ECS/ContainerInsights"
      period      = "120"
      stat        = "Sum"
      dimensions = {
        ClusterName = aws_ecs_cluster.mapi.name
        ServiceName = aws_ecs_service.mapi.name
      }
    }
  }

  metric_query {
    id = "cpu_total"
    metric {
      metric_name = "CpuReserved"
      namespace   = "ECS/ContainerInsights"
      period      = "120"
      stat        = "Sum"
      dimensions = {
        ClusterName = aws_ecs_cluster.mapi.name
        ServiceName = aws_ecs_service.mapi.name
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "memory_utilization" {
  alarm_name                = "${local.mapi_scoped_name}-memory-utilization-too-high"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  threshold                 = "80"
  alarm_description         = "This metric monitors fargate instance memory utilization"
  alarm_actions             = [var.pager_duty_sns_topic_arn]

  metric_query {
    id = "utilizedPercent"
    expression = "memory_used * 100/memory_total"
    label = "Memory Utilization percentage"
    return_data = true
  }

  metric_query {
    id = "memory_used"
    metric {
      metric_name = "MemoryUtilized"
      namespace   = "ECS/ContainerInsights"
      period      = "120"
      stat        = "Sum"
      dimensions = {
          ClusterName = aws_ecs_cluster.mapi.name
          ServiceName = aws_ecs_service.mapi.name
      }
    }
  }

  metric_query {
    id = "memory_total"
    metric {
      metric_name = "MemoryReserved"
      namespace   = "ECS/ContainerInsights"
      period      = "120"
      stat        = "Sum"
      dimensions = {
        ClusterName = aws_ecs_cluster.mapi.name
        ServiceName = aws_ecs_service.mapi.name
      }
    }
  }
}

resource "aws_cloudwatch_metric_alarm" "response500s" {
  alarm_name                = "${local.mapi_scoped_name}-response-500s"
  comparison_operator       = "GreaterThanOrEqualToThreshold"
  evaluation_periods        = "1"
  threshold                 = "1"
  alarm_description         = "This metric monitors fargate instance response 500s"
  alarm_actions             = [var.pager_duty_sns_topic_arn]

  metric_query {
    id = "response500s"
    expression  = "SELECT SUM(${terraform.workspace}_500) FROM CWAgent WHERE metric_type = 'counter'"
    period      = "120"
    return_data = true
  }
}
