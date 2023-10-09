# s3 bucket that stores the resources
resource "aws_s3_bucket" "source" {
  bucket = var.bucket_name

  force_destroy = true
}

resource "aws_s3_bucket_policy" "allow_access_to_cloudfront" {
  bucket = aws_s3_bucket.source.id
  policy = data.aws_iam_policy_document.allow_access_to_cloudfront.json
}

data "aws_iam_policy_document" "allow_access_to_cloudfront" {
    statement {
        sid = "AllowCloudFrontServicePrincipalReadOnly"

        actions = ["s3:GetObject"]
        resources = [
          "${aws_s3_bucket.source.arn}/*"
        ]

        principals {
          type        = "Service"
          identifiers = ["cloudfront.amazonaws.com"]
        }

        condition {
          test     = "StringEquals"
          variable = "aws:SourceArn"
          values   = [aws_cloudfront_distribution.source.arn]
        }
    }
}

resource "aws_acm_certificate" "this" {
  provider = aws.us-east-1
  domain_name       = var.domain_name
  validation_method = "DNS"
}

resource "aws_acm_certificate_validation" "this" {
  provider = aws.us-east-1
  certificate_arn = aws_acm_certificate.this.arn
}

resource "aws_cloudfront_origin_access_control" "this" {
  name                              = "cdn-origin-access-control"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

# cloudfront distribution for serving fe resources from s3 bucket above
resource "aws_cloudfront_distribution" "source" {
  origin {
    domain_name = aws_s3_bucket.source.bucket_regional_domain_name
    origin_id   = aws_s3_bucket.source.id

    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  aliases = [var.domain_name]

  # AWS Managed Caching Policy (CachingOptimized)
  default_cache_behavior {
    # Using the CachingOptimized managed policy ID:
    # https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/using-managed-cache-policies.html#managed-cache-policies-list
    cache_policy_id = "658327ea-f89d-4fab-a63d-7e88639e58f6"
    allowed_methods = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = aws_s3_bucket.source.id
    cached_methods = ["GET", "HEAD", "OPTIONS"]
    viewer_protocol_policy = "redirect-to-https"
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn = aws_acm_certificate.this.arn
    ssl_support_method = "sni-only"
  }
}