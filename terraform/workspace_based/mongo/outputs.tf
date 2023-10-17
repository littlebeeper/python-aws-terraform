output "mongodbatlas_cluster_connection_strings_standard_srv" {
  value = mongodbatlas_serverless_instance.this.connection_strings_standard_srv
}

output "mongodbatlas_cluster_connection_strings_private_endpoint_srv" {
  value = mongodbatlas_serverless_instance.this.connection_strings_private_endpoint_srv
}

output "db_user_admin_password_secrets_manager_key" {
  value = aws_secretsmanager_secret.secrets_manager_entry_admin_user_password.name
}
