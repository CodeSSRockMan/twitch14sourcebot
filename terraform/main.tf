# Terraform main configuration for VPC, Private Subnet, EC2, and S3
provider "aws" {
  region = var.aws_region
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = {
    Name = "twitch14sourcebot-vpc"
  }
}

resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = var.public_subnet_cidr
  # Not mapping public IPs, so this is a private subnet
  map_public_ip_on_launch = false
  tags = {
    Name = "twitch14sourcebot-private-subnet"
  }
}

resource "aws_security_group" "ec2_sg" {
  vpc_id = aws_vpc.main.id
  description = "Allow SSH and HTTP"
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "twitch14sourcebot-ec2-sg"
  }
}

resource "aws_instance" "twitch14_ec2" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = aws_subnet.private.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]
  associate_public_ip_address = false
  tags = {
    Name = "twitch14sourcebot-ec2"
  }
}

resource "aws_s3_bucket" "artifacts" {
  bucket = var.s3_bucket_name
  acl    = "private"
  tags = {
    Name = "twitch14sourcebot-artifacts"
  }
}
