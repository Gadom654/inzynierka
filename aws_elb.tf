resource "aws_elb" "example" {
  name               = "example-elb"
  availability_zones = ["eu-central-1a", "eu-central-1b"]

  listener {
    instance_port     = 80
    instance_protocol = "HTTP"
    lb_port           = 80
    lb_protocol       = "HTTP"
  }

  health_check {
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 3
    target              = "HTTP:80/"
    interval            = 30
  }
  instances = var.active_deployment == "green" ? [aws_instance.green.id] : [aws_instance.blue.id]
}

