# This is the role under which ECS will execute our task. This role becomes more important
# as we add integrations with other AWS services later on.

# The assume_role_policy field works with the following aws_iam_policy_document to allow
# ECS tasks to assume this role we're creating.
resource "aws_iam_role" "mapi_task_execution_role" {
  name               = "${var.name}-task-execution-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_assume_role.json
}

data "aws_iam_policy_document" "ecs_task_execution_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

# Attach the above policy to the execution role.
resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.mapi_task_execution_role.name
  policy_arn = data.aws_iam_policy.ecs_task_execution_role.arn
}

# Define policy to allow access to s3 bucket w/ environment variable file
resource "aws_iam_policy" "s3_read_only_env_bucket_access" {
  name        = "${var.name}s3-read-only-access"
  description = "Read-only access to S3 env bucket"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:Get*",
          "s3:List*",
          "s3-object-lambda:Get*",
          "s3-object-lambda:List*",
        ]
        Effect   = "Allow"
#        Resource = "${aws_s3_bucket.mapi_env.arn}/*"
        Resource = "*"
      },
    ]
  })
}

# Gives s3 read access to the execution role so that we can pull in env values
resource "aws_iam_role_policy_attachment" "task_execution_s3_read_only_access" {
  role       = aws_iam_role.mapi_task_execution_role.name
  policy_arn = aws_iam_policy.s3_read_only_env_bucket_access.arn
}

resource "aws_iam_role_policy_attachment" "task_execution_secrets_manager_access" {
  role       = aws_iam_role.mapi_task_execution_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "task_execution_ssm_read_only_access" {
  role       = aws_iam_role.mapi_task_execution_role.name
  policy_arn = data.aws_iam_policy.ssm_readonly_access.arn
}
