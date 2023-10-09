resource "random_password" "admin_user_password" {
  length  = 64
  special = false
}

resource "aws_secretsmanager_secret" "secrets_manager_entry_admin_user_password" {
  name = "${var.name}/mongo/admin_user_password"
  description = "MongoDB admin user password for ${mongodbatlas_serverless_instance.mapi_db_instance.name}"
  recovery_window_in_days = 0
}

resource "aws_secretsmanager_secret_version" "admin_user_password" {
  secret_id     = aws_secretsmanager_secret.secrets_manager_entry_admin_user_password.id
  secret_string = random_password.admin_user_password.result
}
