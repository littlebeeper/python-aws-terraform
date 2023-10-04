locals {
  api_url = {
    qa         = "api.qa.mogara.com"
    production = "api.mogara.com"
  }
  mapi_scoped_name = "mapi-${terraform.workspace}"
  # for now, keeping the same integration_key for both qa and production
  # b/c pagerduty freemium only allows 1 integration
  pagerduty_integration_secret_id = "global/pagerduty/integration_key"
  mogara_region = "us-west-1"
}
