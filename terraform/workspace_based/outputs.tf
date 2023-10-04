output "server_outgoing_ip" {
  value = module.network.public_outgoing_ip
}

output "domain_validations" {
    value = module.webserver.domain_validations
}

output "db_connection_strings_standard_srv" {
  value = module.db.mongodbatlas_cluster_connection_strings_standard_srv
}

output "db_connection_strings_private_srv" {
  value = module.db.mongodbatlas_cluster_connection_strings_private_endpoint_srv
}

output "db_user_admin_password_secrets_manager_key" {
  value = module.db.user_admin_password_secrets_manager_key
}

output "alb_dns_name" {
  value = module.webserver.alb_dns_name
}

output "activity_capture_lambda_s3_bucket" {
  value = module.activity_capture_lambda.lambda_bucket_name
}

output "activity_capture_lambda_s3_archive_file" {
  value = module.activity_capture_lambda.lambda_s3_archive_file
}

output "activity_capture_lambda_api_gateway_base_url" {
  value = module.activity_capture_lambda.api_gateway_base_url
}

