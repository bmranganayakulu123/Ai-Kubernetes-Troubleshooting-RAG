terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }

    local = {
      source  = "hashicorp/local"
      version = "~> 2.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# ---------------------------------------------------------
# DATA SOURCES
# ---------------------------------------------------------

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ---------------------------------------------------------
# S3 BUCKET
# Replaces Linode Object Storage Bucket
# ---------------------------------------------------------

resource "aws_s3_bucket" "documents" {
  bucket = var.s3_bucket_name

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-documents"
    }
  )
}

# S3 Versioning

resource "aws_s3_bucket_versioning" "documents" {
  bucket = aws_s3_bucket.documents.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 Encryption

resource "aws_s3_bucket_server_side_encryption_configuration" "documents" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block Public Access

resource "aws_s3_bucket_public_access_block" "documents" {
  bucket = aws_s3_bucket.documents.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# ---------------------------------------------------------
# RDS SECURITY GROUP
# Used by both PostgreSQL databases
# ---------------------------------------------------------

resource "aws_security_group" "rds" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RAG PostgreSQL databases"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "PostgreSQL from VPC"
    protocol    = "tcp"
    from_port   = 5432
    to_port     = 5432
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    description = "Allow outbound traffic"
    protocol    = "-1"
    from_port   = 0
    to_port     = 0
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

# ---------------------------------------------------------
# RDS SUBNET GROUP
# ---------------------------------------------------------

resource "aws_db_subnet_group" "rag" {
  name = "${var.project_name}-db-subnet-group"

  subnet_ids = data.aws_subnets.default.ids

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-db-subnet-group"
    }
  )
}

# ---------------------------------------------------------
# VECTOR DATABASE
# Replaces Linode Vector PostgreSQL Database
# ---------------------------------------------------------

resource "aws_db_instance" "vector_db" {
  identifier = "${var.project_name}-vector-db"

  engine         = "postgres"
  engine_version = var.postgres_engine_version

  instance_class = var.postgres_instance_class

  allocated_storage     = var.postgres_allocated_storage
  max_allocated_storage = var.postgres_max_allocated_storage

  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.vector_db_name
  username = var.postgres_username
  password = var.postgres_password

  port = 5432

  db_subnet_group_name = aws_db_subnet_group.rag.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  backup_retention_period = var.backup_retention_period

  skip_final_snapshot = true

  deletion_protection = false

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-vector-db"
    }
  )
}

# ---------------------------------------------------------
# CONVERSATION DATABASE
# Replaces Linode Conversation PostgreSQL Database
# ---------------------------------------------------------

resource "aws_db_instance" "conversation_db" {
  identifier = "${var.project_name}-conversation-db"

  engine         = "postgres"
  engine_version = var.postgres_engine_version

  instance_class = var.postgres_instance_class

  allocated_storage     = var.postgres_allocated_storage
  max_allocated_storage = var.postgres_max_allocated_storage

  storage_type      = "gp3"
  storage_encrypted = true

  db_name  = var.conversation_db_name
  username = var.postgres_username
  password = var.postgres_password

  port = 5432

  db_subnet_group_name = aws_db_subnet_group.rag.name

  vpc_security_group_ids = [
    aws_security_group.rds.id
  ]

  publicly_accessible = false

  backup_retention_period = var.backup_retention_period

  skip_final_snapshot = true

  deletion_protection = false

  tags = merge(
    var.tags,
    {
      Name = "${var.project_name}-conversation-db"
    }
  )
}

# ---------------------------------------------------------
# EKS IAM ROLE
# ---------------------------------------------------------

resource "aws_iam_role" "eks_cluster_role" {
  name = "${var.project_name}-eks-cluster-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "eks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# ---------------------------------------------------------
# EKS NODE IAM ROLE
# ---------------------------------------------------------

resource "aws_iam_role" "eks_node_role" {
  name = "${var.project_name}-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "ec2.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cni_policy" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "eks_container_registry_policy" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# ---------------------------------------------------------
# EKS CLUSTER
# Replaces Linode LKE Cluster
# ---------------------------------------------------------

resource "aws_eks_cluster" "rag_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster_role.arn

  version = var.kubernetes_version

  vpc_config {
    subnet_ids = data.aws_subnets.default.ids
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]

  tags = var.tags
}

# ---------------------------------------------------------
# EKS NODE GROUP
# Replaces Linode LKE Node Pool
# ---------------------------------------------------------

resource "aws_eks_node_group" "rag_nodes" {
  cluster_name = aws_eks_cluster.rag_cluster.name

  node_group_name = "${var.cluster_name}-node-group"

  node_role_arn = aws_iam_role.eks_node_role.arn

  subnet_ids = data.aws_subnets.default.ids

  instance_types = [
    var.eks_node_instance_type
  ]

  scaling_config {
    desired_size = var.eks_node_count
    min_size     = var.eks_autoscaler_min
    max_size     = var.eks_autoscaler_max
  }

  tags = var.tags

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy
  ]
}

# ---------------------------------------------------------
# IAM ROLE FOR EKS PODS
# Gives RAG application access to S3
# ---------------------------------------------------------

resource "aws_iam_role" "rag_s3_role" {
  name = "${var.project_name}-s3-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "eks.amazonaws.com"
        }

        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = var.tags
}

# ---------------------------------------------------------
# S3 ACCESS POLICY
# ---------------------------------------------------------

resource "aws_iam_role_policy" "rag_s3_policy" {
  name = "${var.project_name}-s3-access-policy"

  role = aws_iam_role.rag_s3_role.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject"
        ]

        Resource = "${aws_s3_bucket.documents.arn}/*"
      },
      {
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = aws_s3_bucket.documents.arn
      }
    ]
  })
}

# ---------------------------------------------------------
# KUBECONFIG
# ---------------------------------------------------------

data "aws_eks_cluster_auth" "rag_cluster" {
  name = aws_eks_cluster.rag_cluster.name
}

resource "local_file" "kubeconfig" {
  filename = "${path.module}/kubeconfig.yaml"

  content = templatefile(
    "${path.module}/kubeconfig.tpl",
    {
      cluster_name     = aws_eks_cluster.rag_cluster.name
      cluster_endpoint = aws_eks_cluster.rag_cluster.endpoint
      cluster_ca       = aws_eks_cluster.rag_cluster.certificate_authority[0].data
      region           = var.aws_region
    }
  )

  file_permission = "0600"
} 