resource "aws_route53_zone" "this" {
  name = "jaygokhale.com"
}
# zone id: Z08808412YQZTEMW1K7J8

#jaygokhale.com. 	300 	A 	185.199.108.153
#jaygokhale.com. 	300 	A 	185.199.109.153
#jaygokhale.com. 	300 	A 	185.199.110.153
#jaygokhale.com. 	300 	A 	185.199.111.153
#jaygokhale.com. 	172800 	NS 	ns-1108.awsdns-10.org.
#jaygokhale.com. 	172800 	NS 	ns-1923.awsdns-48.co.uk.
#jaygokhale.com. 	172800 	NS 	ns-812.awsdns-37.net.
#jaygokhale.com. 	172800 	NS 	ns-48.awsdns-06.com.
#jaygokhale.com. 	900 	SOA 	ns-1108.awsdns-10.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400
#_propelauth_verification.staging.jaygokhale.com. 	300 	TXT 	"propelauth_verification=oV4SVeX6VUgo-mWFfC3z9d8x_iazUE2CSFPKJwFWxfKIwtXJ5oLyoIQCLYn1VWjhxbNKCjZ7is2RV6QDT-U4t7y-IvukQr31c_vEoxY752ofnXyWQUoBN-IfraIRGp3Y"
#api.staging.jaygokhale.com. 	300 	CNAME 	jaygokhale-api-staging-lb-1937399453.us-west-1.elb.amazonaws.com.
#_335efbdec163679c0fdf84327ad9f337.api.staging.jaygokhale.com. 	300 	CNAME 	_b176837c6cbddc47393ddeb6fe189e36.smwfzlpyzn.acm-validations.aws.
#auth.staging.jaygokhale.com. 	300 	CNAME 	ext.propelauth.com.
#dashboard.staging.jaygokhale.com. 	300 	CNAME 	d14vqr8jcg6vx0.cloudfront.net.
#_2d6b23e10bff5b70a34e8fe27f606460.dashboard.staging.jaygokhale.com. 	300 	CNAME 	_19d8cfd187729c66fce14286da9137e7.smwfzlpyzn.acm-validations.aws.

resource "aws_route53_record" "a_records" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "jaygokhale.com"
  type    = "A"
  ttl     = "300"
  records = ["185.199.108.153", "185.199.109.153", "185.199.110.153", "185.199.111.153"]
}
# terraform import aws_route53_record.a_records Z08808412YQZTEMW1K7J8_jaygokhale.com_A

# NS records
resource "aws_route53_record" "ns_records" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "jaygokhale.com"
  type    = "NS"
  ttl     = "172800"
  records = ["ns-1108.awsdns-10.org.", "ns-1923.awsdns-48.co.uk.", "ns-812.awsdns-37.net.", "ns-48.awsdns-06.com."]
}
# terraform import aws_route53_record.ns_records Z08808412YQZTEMW1K7J8_jaygokhale.com_NS

resource "aws_route53_record" "soa_records" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "jaygokhale.com"
  type    = "SOA"
  ttl     = "900"
  records = ["ns-1108.awsdns-10.org. awsdns-hostmaster.amazon.com. 1 7200 900 1209600 86400"]
}
# terraform import aws_route53_record.soa_records Z08808412YQZTEMW1K7J8_jaygokhale.com_SOA

# dashboard redirect to cloudfront
resource "aws_route53_record" "fe_redirect" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "dashboard.staging.jaygokhale.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["d14vqr8jcg6vx0.cloudfront.net."]
}
# terraform import aws_route53_record.fe_redirect Z08808412YQZTEMW1K7J8_dashboard.staging.jaygokhale.com_CNAME

# ACM validation for dashboard
resource "aws_route53_record" "dashboard_acm_validation" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "_2d6b23e10bff5b70a34e8fe27f606460.dashboard.staging.jaygokhale.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["_19d8cfd187729c66fce14286da9137e7.smwfzlpyzn.acm-validations.aws."]
}
# terraform import aws_route53_record.dashboard_acm_validation Z08808412YQZTEMW1K7J8__2d6b23e10bff5b70a34e8fe27f606460.dashboard.staging.jaygokhale.com_CNAME

# api redirect to load balancer
resource "aws_route53_record" "api_redirect" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "api.staging.jaygokhale.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["jaygokhale-api-staging-lb-1937399453.us-west-1.elb.amazonaws.com."]
}
# terraform import aws_route53_record.api_redirect Z08808412YQZTEMW1K7J8_api.staging.jaygokhale.com_CNAME

# ACM validation for api
resource "aws_route53_record" "api_acm_validation" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "_335efbdec163679c0fdf84327ad9f337.api.staging.jaygokhale.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["_b176837c6cbddc47393ddeb6fe189e36.smwfzlpyzn.acm-validations.aws."]
}
# terraform import aws_route53_record.api_acm_validation Z08808412YQZTEMW1K7J8__335efbdec163679c0fdf84327ad9f337.api.staging.jaygokhale.com_CNAME

# propel auth validation
resource "aws_route53_record" "propel_auth_validation" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "_propelauth_verification.staging.jaygokhale.com"
  type    = "TXT"
  ttl     = "300"
  records = ["propelauth_verification=oV4SVeX6VUgo-mWFfC3z9d8x_iazUE2CSFPKJwFWxfKIwtXJ5oLyoIQCLYn1VWjhxbNKCjZ7is2RV6QDT-U4t7y-IvukQr31c_vEoxY752ofnXyWQUoBN-IfraIRGp3Y"]
}
# terraform import aws_route53_record.propel_auth_validation Z08808412YQZTEMW1K7J8__propelauth_verification.staging.jaygokhale.com_TXT

# auth redirect to propel
resource "aws_route53_record" "auth_redirect" {
  zone_id = aws_route53_zone.this.zone_id
  name    = "auth.staging.jaygokhale.com"
  type    = "CNAME"
  ttl     = "300"
  records = ["ext.propelauth.com."]
}
# terraform import aws_route53_record.auth_redirect Z08808412YQZTEMW1K7J8_auth.staging.jaygokhale.com_CNAME