resource "aws_ecr_registry_scanning_configuration" "enhanced_container_scanning" {
  scan_type = "ENHANCED"

  rule {
    scan_frequency = "SCAN_ON_PUSH"
    repository_filter {
      filter      = "production"
      filter_type = "WILDCARD"
    }
  }
}
