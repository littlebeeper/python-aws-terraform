provider "aws" {
  region = "us-west-1"
}

resource "aws_ecr_repository" "this" {
  name = var.lambda_function_name
}

resource "aws_lambda_function" "lambda_function" {
  function_name = var.lambda_function_name
  timeout       = 900
  image_uri     = "${aws_ecr_repository.this.repository_url}:latest"
  package_type  = "Image"

  vpc_config {
    security_group_ids = [var.egress_security_group_id]
    subnet_ids = var.private_subnet_ids
  }

  role = aws_iam_role.function_role.arn
}

resource "aws_iam_role" "function_role" {
  name = "${var.lambda_function_name}_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name = "/aws/lambda/${aws_lambda_function.lambda_function.function_name}"

  retention_in_days = 365
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.function_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "lambda_vpc_policy" {
  role       = aws_iam_role.function_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}

resource "aws_iam_policy" "secrets_manager_access" {
  name        = "${var.lambda_function_name}_secrets_manager_access"
  description = "Allows access to secrets manager for ${var.lambda_function_name}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "secretsmanager:GetResourcePolicy",
          "secretsmanager:GetSecretValue",
          "secretsmanager:DescribeSecret",
          "secretsmanager:ListSecretVersionIds"
        ]
        Effect   = "Allow"
#        Resource = "arn:aws:secretsmanager:us-west-1:940730671260:secret:dev/*"
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_manager_access" {
  role       = aws_iam_role.function_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

resource "aws_iam_policy" "s3_access" {
    name        = "${var.lambda_function_name}_s3_access"
    description = "Allows access to s3 for ${var.lambda_function_name}"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Action = [
            "s3:GetObject",
            "s3:PutObject",
            "s3:DeleteObject",
            "s3:ListBucket"
            ]
            Effect   = "Allow"
            Resource = "*"
        },
        ]
    })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
    role       = aws_iam_role.function_role.name
    policy_arn = aws_iam_policy.s3_access.arn
}

resource "aws_iam_policy" "sns_topic_publish_access" {
    name        = "${var.lambda_function_name}_sns_topic_publish_access"
    description = "Allows access to publish to sns topic for ${var.lambda_function_name}"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Action = [
            "sns:Publish"
            ]
            Effect   = "Allow"
            Resource = var.pager_duty_sns_topic_arn
        },
        ]
    })
}

resource "aws_iam_role_policy_attachment" "sns_topic_publish_access" {
    role       = aws_iam_role.function_role.name
    policy_arn = aws_iam_policy.sns_topic_publish_access.arn
}
