output "server_outgoing_ip" {
  value = module.network.public_outgoing_ip
}

output "domain_validations" {
    value = module.api_server.domain_validations
}

output "db_connection_strings_standard_srv" {
  value = module.db.mongodbatlas_cluster_connection_strings_standard_srv
}

output "db_connection_strings_private_srv" {
  value = module.db.mongodbatlas_cluster_connection_strings_private_endpoint_srv
}

output "db_user_admin_password_secrets_manager_key" {
  value = module.db.db_user_admin_password_secrets_manager_key
}

output "alb_dns_name" {
  value = module.api_server.alb_dns_name
}

output "jaygokhale_fe_domain_name" {
  value = module.frontend_cdn.distribution_domain_name
}
