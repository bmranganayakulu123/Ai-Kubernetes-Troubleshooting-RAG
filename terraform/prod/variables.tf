variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "ai-kubernetes-troubleshooting-rag"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.20.0.0/16"
}

variable "availability_zones" {
  description = "Availability Zones"
  type        = list(string)

  default = [
    "ap-northeast-2a",
    "ap-northeast-2c"
  ]
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs"
  type        = list(string)

  default = [
    "10.20.1.0/24",
    "10.20.2.0/24"
  ]
}

variable "private_app_subnet_cidrs" {
  description = "Private EKS subnet CIDRs"
  type        = list(string)

  default = [
    "10.20.11.0/24",
    "10.20.12.0/24"
  ]
}

variable "private_db_subnet_cidrs" {
  description = "Private RDS subnet CIDRs"
  type        = list(string)

  default = [
    "10.20.21.0/24",
    "10.20.22.0/24"
  ]
}

variable "tags" {
  description = "Common tags"
  type        = map(string)

  default = {
    Project     = "AI-Kubernetes-Troubleshooting-RAG"
    Environment = "prod"
    ManagedBy   = "Terraform"
  }
}

variable "postgres_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16"
}

variable "postgres_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "postgres_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "ragadmin"
}

variable "initial_database_name" {
  description = "Initial database created by RDS"
  type        = string
  default     = "vectordb"
}

variable "postgres_allocated_storage" {
  description = "Initial RDS storage in GB"
  type        = number
  default     = 20
}

variable "postgres_max_allocated_storage" {
  description = "Maximum autoscaled RDS storage in GB"
  type        = number
  default     = 100
}

variable "backup_retention_period" {
  description = "RDS backup retention in days"
  type        = number
  default     = 7
}

variable "document_bucket_name" {
  description = "Globally unique S3 bucket for RAG documents"
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "ai-k8s-rag-prod"
}

variable "kubernetes_version" {
  description = "EKS Kubernetes version"
  type        = string
  default     = "1.35"
}

variable "eks_node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "eks_node_desired_size" {
  description = "Desired number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "eks_node_min_size" {
  description = "Minimum number of EKS worker nodes"
  type        = number
  default     = 1
}

variable "eks_node_max_size" {
  description = "Maximum number of EKS worker nodes"
  type        = number
  default     = 3
}