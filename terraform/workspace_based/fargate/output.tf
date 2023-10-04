output "api_domain" {
  value = local.api_url[terraform.workspace]
}

output "domain_validations" {
    value = aws_acm_certificate.mapi.domain_validation_options
}

output "alb_dns_name" {
  value = aws_alb.mapi.dns_name
}
