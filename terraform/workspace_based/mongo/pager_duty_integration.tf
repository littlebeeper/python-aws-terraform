 # service key in aws secrets manager
 data "aws_secretsmanager_secret" "pg_service_key" {
     name = "${terraform.workspace}/pager_duty/mongo_atlas_integration_key"
 }

 data "aws_secretsmanager_secret_version" "pg_service_key" {
     secret_id = data.aws_secretsmanager_secret.pg_service_key.id
 }

resource "mongodbatlas_third_party_integration" "pagerduty_integration" {
    project_id = mongodbatlas_project.mapi_db_project.id
    # type of integration
    type = "PAGER_DUTY"

    service_key = data.aws_secretsmanager_secret_version.pg_service_key.secret_string
}

# alert configuration: connections > 80% of max connections
# configuration fails with
#╷
#│ Error: Provider produced inconsistent final plan
#│
#│ When expanding the plan for module.db.mongodbatlas_alert_configuration.connections_alert to include new values learned so far during apply, provider
#│ "registry.terraform.io/mongodb/mongodbatlas" produced an invalid new value for .notification[0].service_key: inconsistent values for sensitive attribute.
#│
#│ This is a bug in the provider, which should be reported in the provider's own issue tracker.
#╵
# resource "mongodbatlas_alert_configuration" "connections_alert" {
#   project_id = mongodbatlas_project.mapi_db_project.id
#   enabled = true
#   event_type = "OUTSIDE_SERVERLESS_METRIC_THRESHOLD"
#   metric_threshold_config {
#     metric_name = "SERVERLESS_CONNECTIONS_PERCENT"
#     operator = "GREATER_THAN"
#     threshold = 80
#     units = "RAW"
#     mode = "AVERAGE"
#  }
#
#    notification {
#      type_name = "PAGER_DUTY"
#      service_key = mongodbatlas_third_party_integration.pagerduty_integration.service_key
#      delay_min = 0
#    }
# }