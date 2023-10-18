resource "aws_flow_log" "example" {
  log_destination      = aws_s3_bucket.flow_logs_bucket.arn
  log_destination_type = "s3"
  traffic_type         = "ALL"
  vpc_id               = aws_vpc.vpc.id
}

resource "aws_s3_bucket" "flow_logs_bucket" {
  bucket = "vpc-flow-logs-${var.name}"
}