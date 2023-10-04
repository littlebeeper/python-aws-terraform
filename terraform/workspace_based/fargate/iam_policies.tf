# Normally we'd prefer not to hardcode an ARN in our Terraform, but since this is an AWS-managed
# policy, it's okay.
data "aws_iam_policy" "ecs_task_execution_role" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy" "cloudwatch_agent_server_policy" {
  arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

data "aws_iam_policy" "ssm_readonly_access" {
  arn = "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess"
}

resource "aws_iam_policy" "secrets_manager_access" {
  name        = "${local.mapi_scoped_name}-secrets-manager-access"
  description = "Allows access to secrets manager for ${local.mapi_scoped_name}"
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

resource "aws_iam_policy" "invoke_lambda_access" {
    name = "${local.mapi_scoped_name}-invoke-lambda-access"
    description = "Allows access to invoke lambda for ${local.mapi_scoped_name}"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
        {
            Action = [
            "lambda:InvokeFunction"
            ]
            Effect   = "Allow"
            Resource = "*"
        },
        ]
    })
}

resource "aws_iam_policy" "aws_exec_access" {
  name = "${local.mapi_scoped_name}-aws-exec-access"
  description = "Allows access to AWS exec for tasks in ${local.mapi_scoped_name}"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ssmmessages:CreateControlChannel",
          "ssmmessages:CreateDataChannel",
          "ssmmessages:OpenControlChannel",
          "ssmmessages:OpenDataChannel"
        ]
        Effect   = "Allow"
        Resource = "*"
      },
    ]
  })
}
