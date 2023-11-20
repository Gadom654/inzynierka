resource "aws_iam_policy" "dynamodb_policy" {
  name        = "DynamoDBFullAccessPolicy"
  description = "Policy to grant full access to DynamoDB"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action   = "dynamodb:*",
        Effect   = "Allow",
        Resource = "*"
      },
    ]
  })
}

resource "aws_iam_role" "ec2_dynamodb_role" {
  name = "ec2_dynamodb_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = "sts:AssumeRole",
        Effect = "Allow",
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_dynamodb" {
  role       = aws_iam_role.ec2_dynamodb_role.name
  policy_arn = aws_iam_policy.dynamodb_policy.arn
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "ec2_dynamodb_profile"
  role = aws_iam_role.ec2_dynamodb_role.name
}

resource "aws_instance" "test_terraform" {
  ami                                  = "ami-0a485299eeb98b979"
  associate_public_ip_address          = true
  availability_zone                    = "eu-central-1a"
  disable_api_stop                     = false
  disable_api_termination              = false
  ebs_optimized                        = false
  get_password_data                    = false
  hibernation                          = false
  host_id                              = null
  host_resource_group_arn              = null
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  instance_initiated_shutdown_behavior = "stop"
  instance_type                        = "t2.micro"
  key_name                             = "flaskin"
  monitoring                           = false
  placement_group                      = null
  placement_partition_number           = 0
  private_ip                           = "172.31.30.244"
  secondary_private_ips                = []
  source_dest_check                    = true
  subnet_id                            = "subnet-0fc7a835e988235bb"
  tags = {
    Name = "FlaskApp"
  }
  tags_all = {
    Name = "FlaskApp"
  }
  tenancy                     = "default"
  volume_tags                 = null
  vpc_security_group_ids      = ["sg-0d66a533b925c44f5"]
  capacity_reservation_specification {
    capacity_reservation_preference = "open"
  }
  credit_specification {
    cpu_credits = "standard"
  }
  enclave_options {
    enabled = false
  }
  maintenance_options {
    auto_recovery = "default"
  }
  metadata_options {
    http_endpoint               = "enabled"
    http_protocol_ipv6          = "disabled"
    http_put_response_hop_limit = 2
    http_tokens                 = "required"
    instance_metadata_tags      = "disabled"
  }
  private_dns_name_options {
    enable_resource_name_dns_a_record    = true
    enable_resource_name_dns_aaaa_record = false
    hostname_type                        = "ip-name"
  }
  root_block_device {
    delete_on_termination = true
    encrypted             = false
    iops                  = 3000
    kms_key_id            = null
    tags                  = {}
    throughput            = 125
    volume_size           = 8
    volume_type           = "gp3"
  }
    user_data = <<-EOF
#!/bin/bash
sudo yum install -y httpd pip git httpd-devel python3-devel
cd /tmp
git clone https://github.com/Gadom654/inzynierka
mv /tmp/inzynierka/stock_app /stock_app
sudo mv /tmp/inzynierka/flask.conf /etc/httpd/conf.d/flask.conf
cd /stock_app
ln -s /usr/bin/python3 /usr/bin/python
python -m venv flask
source flask/bin/activate
pip install -r requirements.txt
sudo systemctl start httpd
EOF
}
