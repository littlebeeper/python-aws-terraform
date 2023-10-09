resource "mongodbatlas_project" "mapi_db_project" {
  name   = "${var.name}-project"
  org_id = "63ae2c9231ce5803703fc5dd"

  is_collect_database_specifics_statistics_enabled = true
  is_data_explorer_enabled                         = true
  is_performance_advisor_enabled                   = true
  is_realtime_performance_panel_enabled            = true
  is_schema_advisor_enabled                        = true
}

resource "mongodbatlas_serverless_instance" "mapi_db_instance" {
  project_id   = mongodbatlas_project.mapi_db_project.id
  name         = "${var.name}-serverless-instance"

  provider_settings_backing_provider_name = "AWS"
  provider_settings_provider_name = "SERVERLESS"
  provider_settings_region_name = "US_WEST_2"
}

resource "mongodbatlas_project_ip_access_list" "webserver_ip_access" {
  project_id = mongodbatlas_project.mapi_db_project.id
  ip_address = var.webserver_ip
  comment    = "${var.name} webserver ip"
}
