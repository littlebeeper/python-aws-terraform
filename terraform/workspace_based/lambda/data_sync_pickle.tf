resource "aws_s3_bucket" "pickle_cache" {
  bucket        = "mogara-pickle-cache-${terraform.workspace}"
  force_destroy = true

  tags = {
    VantaNonProd = terraform.workspace != "production"
    VantaContainsUserData = "true"
  }
}



