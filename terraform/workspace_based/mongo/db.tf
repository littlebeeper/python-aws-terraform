resource "mongodbatlas_project" "this" {
  name   = "${var.name}-project"
  org_id = "63ae2c9231ce5803703fc5dd"

  is_collect_database_specifics_statistics_enabled = true
  is_data_explorer_enabled                         = true
  is_performance_advisor_enabled                   = true
  is_realtime_performance_panel_enabled            = true
  is_schema_advisor_enabled                        = true
}

resource "mongodbatlas_serverless_instance" "this" {
  project_id   = mongodbatlas_project.this.id
  name         = "${var.name}-serverless-instance"

  provider_settings_backing_provider_name = "AWS"
  provider_settings_provider_name = "SERVERLESS"
  provider_settings_region_name = "US_WEST_2"
}

resource "mongodbatlas_project_ip_access_list" "webserver_ip_access" {
  project_id = mongodbatlas_project.this.id
  ip_address = var.webserver_ip
  comment    = "${var.name} webserver ip"
}

data "http" "myip" {
  url = "http://ipv4.icanhazip.com"
}

resource "mongodbatlas_project_ip_access_list" "my_ip_access" {
  project_id = mongodbatlas_project.this.id
  ip_address = chomp(data.http.myip.response_body)
  comment    = "allows my ip to access ${var.name} db"
}