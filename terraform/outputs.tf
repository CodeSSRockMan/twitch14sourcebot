output "ec2_public_ip" {
  value = aws_instance.twitch14_ec2.public_ip
}

output "s3_bucket_name" {
  value = aws_s3_bucket.artifacts.bucket
}
