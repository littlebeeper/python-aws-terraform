resource "aws_lb_target_group" "mapi" {
  name        = local.mapi_scoped_name
  port        = 80
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id

  health_check {
    enabled = true
    path    = "/health"
    interval = 300
  }

#  lifecycle {
#    create_before_destroy = true
#  }

  depends_on = [aws_alb.mapi]
}

resource "aws_alb" "mapi" {
  name               = "${local.mapi_scoped_name}-lb"
  internal           = false
  load_balancer_type = "application"

  subnets = var.public_subnet_ids

  security_groups = [
    aws_security_group.http.id,
    aws_security_group.https.id,
    var.egress_security_group_id,
  ]

  depends_on = [var.internet_gateway_id]
}

resource "aws_alb_listener" "mapi_http" {
  load_balancer_arn = aws_alb.mapi.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_alb_listener" "mapi_https" {
  load_balancer_arn = aws_alb.mapi.arn
  port              = "443"
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.mapi.arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.mapi.arn
  }
}

resource "aws_acm_certificate" "mapi" {
  domain_name       = local.api_url[terraform.workspace]
  validation_method = "DNS"
}

resource "aws_acm_certificate_validation" "mapi" {
  certificate_arn         = aws_acm_certificate.mapi.arn
}
