resource "aws_iam_role" "mapi_task_role" {
  name = "${local.mapi_scoped_name}-task-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume_role.json
}

data "aws_iam_policy_document" "ecs_task_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "secrets_manager_access" {
  role       = aws_iam_role.mapi_task_role.name
  policy_arn = aws_iam_policy.secrets_manager_access.arn
}

resource "aws_iam_role_policy_attachment" "aws_exec_access" {
  role       = aws_iam_role.mapi_task_role.name
  policy_arn = aws_iam_policy.aws_exec_access.arn
}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs_access" {
  role       = aws_iam_role.mapi_task_role.name
  policy_arn = data.aws_iam_policy.cloudwatch_agent_server_policy.arn
}

resource "aws_iam_role_policy_attachment" "invoke_lambda_access" {
  role       = aws_iam_role.mapi_task_role.name
  policy_arn = aws_iam_policy.invoke_lambda_access.arn
}
