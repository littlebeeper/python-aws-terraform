variable "name" {
  type = string
  description = "Name of this CDN"
}

variable "bucket_name" {
  type = string
  description = "The name of the S3 bucket to use for the CloudFront distribution"
}

variable "domain_name" {
  type = string
  description = "The domain name to use for the CloudFront distribution"
}
