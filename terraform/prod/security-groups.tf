# =========================================================
# OPTIONAL CUSTOM EKS SECURITY GROUP
# Keep temporarily so Terraform does not unexpectedly
# remove resources during this correction.
# =========================================================

resource "aws_security_group" "eks_nodes" {
  name        = "${var.project_name}-${var.environment}-eks-nodes-sg"
  description = "Security group for EKS worker nodes"
  vpc_id      = aws_vpc.main.id

  egress {
    description = "Allow all outbound traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-eks-nodes-sg"
  }
}

# =========================================================
# RDS SECURITY GROUP
# Keep name and description exactly as they exist in state.
# =========================================================

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-${var.environment}-rds-sg"
  description = "Allow PostgreSQL only from EKS nodes"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "PostgreSQL from EKS nodes"
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432

    # Actual EKS-managed cluster security group
    security_groups = [
      aws_eks_cluster.main.vpc_config[0].cluster_security_group_id
    ]
  }

  egress {
    description = "Allow outbound traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-rds-sg"
  }

  lifecycle {
    prevent_destroy = true
  }
}