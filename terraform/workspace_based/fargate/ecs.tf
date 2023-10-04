# We need a cluster in which to put our service.
resource "aws_ecs_cluster" "mapi" {
  name = local.mapi_scoped_name

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    VantaNonProd = terraform.workspace != "production"
  }
}

# An ECR repository is a private alternative to Docker Hub.
resource "aws_ecr_repository" "mapi" {
  name = local.mapi_scoped_name

  tags = {
    VantaNonProd = terraform.workspace != "production"
  }
}

# Log groups hold logs from our app.
resource "aws_cloudwatch_log_group" "mapi" {
  name = "/ecs/${local.mapi_scoped_name}"

  retention_in_days = 365
}

resource "aws_cloudwatch_log_group" "cloudwatch_agent" {
  name = "ecs/${local.mapi_scoped_name}/cloudwatch-agent"

  retention_in_days = 365
}

# The main service.
resource "aws_ecs_service" "mapi" {
  name            = local.mapi_scoped_name
  task_definition = aws_ecs_task_definition.mapi.arn
  cluster         = aws_ecs_cluster.mapi.id
  launch_type     = "FARGATE"

  desired_count = 1
  enable_execute_command = true

  load_balancer {
    target_group_arn = aws_lb_target_group.mapi.arn
    container_name   = local.mapi_scoped_name
    container_port   = "80"
  }

  network_configuration {
    assign_public_ip = false

    security_groups = [
      var.egress_security_group_id,
      aws_security_group.ingress_api.id,
    ]

    subnets = var.private_subnet_ids
  }

  tags = {
    VantaNonProd = terraform.workspace != "production"
    VantaContainsUserData = "true"
  }
}

# The s3 bucket containing our env files.
resource "aws_s3_bucket" "mapi_env" {
  bucket        = "mogara-api-env-${terraform.workspace}"

  force_destroy = true

  tags = {
    VantaNonProd = terraform.workspace != "production"
  }
}

# block all public access
resource "aws_s3_bucket_public_access_block" "mapi_env" {
  bucket = aws_s3_bucket.mapi_env.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_ssm_parameter" "mapi_cloudwatch_agent_configuration" {
  name        = "/${local.mapi_scoped_name}/cloudwatch/config"
  description = "CloudWatch Agent configuration for ${local.mapi_scoped_name}"
  type        = "String"
  value       = jsonencode({
    "agent" : {
      "metrics_collection_interval" : 60,
      "region" : "${local.mogara_region}",
      "logfile" : "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log",
      "debug" : true
    },
    "metrics" : {
      "metrics_collected": {
        "statsd" : {
          "metrics_aggregation_interval" : 60,
          "metrics_collection_interval" : 10,
          "service_address" : ":8125"
        },
      }
    },
  })
}

# The task definition for our app.
resource "aws_ecs_task_definition" "mapi" {
  family = local.mapi_scoped_name

  task_role_arn = aws_iam_role.mapi_task_role.arn
  container_definitions = jsonencode(
  [
    {
      name: "redis",
      image: "redis",
      portMappings: [
        {
          containerPort: 6379,
        }
      ],
    },
    {
      name: "celery-worker",
      image: "${aws_ecr_repository.mapi.repository_url}:latest",
      command: [
        "celery", "-A", "backend.celery_worker.celery_app", "worker", "--uid", "myuser", "--loglevel=DEBUG",
      ],
      environmentFiles: [
          {
              value: "${aws_s3_bucket.mapi_env.arn}/.env",
              type: "s3"
          }
      ],
      environment: [
        {
          name: "CELERY_BROKER_URL",
          value: "redis://localhost:6379/0"
        }
      ],
      logConfiguration: {
        logDriver: "awslogs",
        options: {
          awslogs-region: local.mogara_region,
          awslogs-group: aws_cloudwatch_log_group.mapi.name,
          awslogs-stream-prefix: "ecs"
        }
      }
    },
    {
      name: local.mapi_scoped_name,
      image: "${aws_ecr_repository.mapi.repository_url}:latest",
      environmentFiles: [
          {
              value: "${aws_s3_bucket.mapi_env.arn}/.env",
              type: "s3"
          }
      ],
      environment: [
        {
          name: "CELERY_BROKER_URL",
          value: "redis://localhost:6379/0"
        }
      ],
      portMappings: [
        {
          containerPort: 80,
        }
      ],
      linuxParameters: {
        initProcessEnabled: true
      },
      logConfiguration: {
        logDriver: "awslogs",
        options: {
          awslogs-region: local.mogara_region,
          awslogs-group: aws_cloudwatch_log_group.mapi.name,
          awslogs-stream-prefix: "ecs"
        }
      }
    },
    {
      name: "cloudwatch-agent",
      image: "public.ecr.aws/cloudwatch-agent/cloudwatch-agent:latest",
      secrets: [
          {
              "name": "CW_CONFIG_CONTENT",
              "valueFrom": "${aws_ssm_parameter.mapi_cloudwatch_agent_configuration.arn}"
          }
      ],
      portMappings: [
        {
          containerPort: 8125
        }
      ],
      linuxParameters: {
        initProcessEnabled: true
      },
      logConfiguration: {
          logDriver: "awslogs",
          options: {
            awslogs-group: "${aws_cloudwatch_log_group.cloudwatch_agent.name}",
            awslogs-region: "${local.mogara_region}",
            awslogs-stream-prefix: "ecs"
          }
      }
    }
  ])

  execution_role_arn = aws_iam_role.mapi_task_execution_role.arn

  # These are the minimum values for Fargate containers.
  cpu                      = 256
  memory                   = 512
  requires_compatibilities = ["FARGATE"]

  # This is required for Fargate containers (more on this later).
  network_mode = "awsvpc"
}
