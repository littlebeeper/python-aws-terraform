output "domain_validations" {
    value = aws_acm_certificate.this.domain_validation_options
}

output "alb_dns_name" {
  value = aws_alb.this.dns_name
}
