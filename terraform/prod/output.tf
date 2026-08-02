output "vpc_id" {
  value = aws_vpc.main.id
}

output "public_subnet_ids" {
  value = aws_subnet.public[*].id
}

output "private_app_subnet_ids" {
  value = aws_subnet.private_app[*].id
}

output "private_db_subnet_ids" {
  value = aws_subnet.private_db[*].id
}

output "rds_endpoint" {
  value = aws_db_instance.rag.address
}

output "rds_port" {
  value = aws_db_instance.rag.port
}

output "rds_master_secret_arn" {
  value     = aws_db_instance.rag.master_user_secret[0].secret_arn
  sensitive = true
}

output "document_bucket_name" {
  value = aws_s3_bucket.documents.bucket
}

output "eks_cluster_name" {
  value = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  value = aws_eks_cluster.main.endpoint
}

output "eks_node_group_name" {
  value = aws_eks_node_group.main.node_group_name
}

output "eks_cluster_security_group_id" {
  value = aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
}

output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions"
  value       = aws_iam_role.github_actions_deploy.arn
}