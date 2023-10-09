module "pager_duty" {
  source = "./pager_duty"
  name   = "jaygokhale-${terraform.workspace}"
}

module "network" {
  source = "./network"
  region = var.region
  name   = "jaygokhale-${terraform.workspace}"
}

module "api_server" {
  name = "jaygokhale-api-${terraform.workspace}"
  source = "./api_server"
  vpc_id = module.network.vpc_id
  region = var.region
  api_url = var.api_url[terraform.workspace]
  pager_duty_sns_topic_arn = module.pager_duty.pager_duty_sns_topic_arn
  egress_security_group_id = module.network.egress_security_group_id
  internet_gateway_id = module.network.internet_gateway_id
  private_subnet_ids = [module.network.private_subnet_a, module.network.private_subnet_c]
  public_subnet_ids = [module.network.public_subnet_a, module.network.public_subnet_c]
  env_bucket_name = "jaygokhale-env-${terraform.workspace}"
  cloudwatch_500s_alarm_name = "${terraform.workspace}_500"
}

module "frontend_cdn" {
  name           = "jaygokhale-fe-assets-${terraform.workspace}"
  source = "./frontend_cdn"
  bucket_name    = "jaygokhale-fe-assets-${terraform.workspace}"
  domain_name    = var.frontend_url[terraform.workspace]
}

module "db" {
  name = "jaygokhale-db-${terraform.workspace}"
  source = "./mongo"
  mongodbatlas_public_key = var.mongodbatlas_public_key
  mongodbatlas_private_key = var.mongodbatlas_private_key
  webserver_ip = module.network.public_outgoing_ip
  pager_duty_service_key = module.pager_duty.service_key
  internet_gateway_id = module.network.internet_gateway_id
  secrets_manager_key_pd_integration_key = "jaygokhale-${terraform.workspace}/pager_duty/mongo_atlas_integration_key"
}

#module "backend_lambda" {
#  source = "./lambda"
#
#  private_subnet_ids = [module.network.private_subnet_a, module.network.private_subnet_c]
#  egress_security_group_id = module.network.egress_security_group_id
#  pager_duty_sns_topic_arn = module.pager_duty_integration.pager_duty_sns_topic_arn
#  lambda_function_name = "recalc-${terraform.workspace}"
#}
