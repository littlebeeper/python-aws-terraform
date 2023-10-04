# network outputs
output "vpc_id" {
  value = aws_vpc.vpc.id
}

output "public_subnet_a" {
  value = aws_subnet.public_a.id
}

output "public_subnet_c" {
  value = aws_subnet.public_c.id
}

output "private_subnet_a" {
  value = aws_subnet.private_a.id
}

output "private_subnet_c" {
  value = aws_subnet.private_c.id
}

output "egress_security_group_id" {
  value = aws_security_group.egress_all.id
}

output "public_outgoing_ip" {
  value = aws_eip.nat.public_ip
}

output "internet_gateway_id" {
  value = aws_internet_gateway.igw.id
}