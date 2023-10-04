module "pager_duty_integration" {
  source = "./pager_duty"
}

module "network" {
  source = "./network"
}


module "webserver" {
  source = "./mapi"
  pager_duty_sns_topic_arn = module.pager_duty_integration.pager_duty_sns_topic_arn
  egress_security_group_id = module.network.egress_security_group_id
  internet_gateway_id = module.network.internet_gateway_id
  private_subnet_ids = [module.network.private_subnet_a, module.network.private_subnet_c]
  public_subnet_ids = [module.network.public_subnet_a, module.network.public_subnet_c]
  vpc_id = module.network.vpc_id
}

module "db" {
  source = "./mongo"
  mongodbatlas_public_key = var.mongodbatlas_public_key
  mongodbatlas_private_key = var.mongodbatlas_private_key
  webserver_ip = module.network.public_outgoing_ip
  pager_duty_service_key = module.pager_duty_integration.service_key
  internet_gateway_id = module.network.internet_gateway_id
}

module "backend_lambda" {
  source = "./backend_lambda"

  private_subnet_ids = [module.network.private_subnet_a, module.network.private_subnet_c]
  egress_security_group_id = module.network.egress_security_group_id
  pager_duty_sns_topic_arn = module.pager_duty_integration.pager_duty_sns_topic_arn
}
