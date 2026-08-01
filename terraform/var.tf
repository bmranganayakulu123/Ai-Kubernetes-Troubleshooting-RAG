# ---------------------------------------------------------
# AWS REGION
# ---------------------------------------------------------

variable "aws_region" {
  description = "AWS region where resources will be created"
  type        = string
  default     = "ap-northeast-2"
}

# ---------------------------------------------------------
# PROJECT
# ---------------------------------------------------------

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "rag-chatbot"
}

variable "tags" {
  description = "Common tags applied to AWS resources"
  type        = map(string)

  default = {
    Project     = "RAG-Chatbot"
    Environment = "dev"
    ManagedBy   = "Terraform"
  }
}

# ---------------------------------------------------------
# S3
# ---------------------------------------------------------

variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name for RAG documents"
  type        = string
}

# ---------------------------------------------------------
# POSTGRESQL / RDS
# ---------------------------------------------------------

variable "postgres_engine_version" {
  description = "PostgreSQL engine version for RDS"
  type        = string
  default     = "16.4"
}

variable "postgres_instance_class" {
  description = "RDS PostgreSQL instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "postgres_allocated_storage" {
  description = "Initial RDS storage in GB"
  type        = number
  default     = 20
}

variable "postgres_max_allocated_storage" {
  description = "Maximum RDS storage in GB"
  type        = number
  default     = 100
}

variable "postgres_username" {
  description = "Master username for PostgreSQL databases"
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "Master password for PostgreSQL databases"
  type        = string
  sensitive   = true
}

variable "vector_db_name" {
  description = "Database name for the RAG vector database"
  type        = string
  default     = "vectordb"
}

variable "conversation_db_name" {
  description = "Database name for conversation/state storage"
  type        = string
  default     = "conversationdb"
}

variable "backup_retention_period" {
  description = "Number of days to retain RDS backups"
  type        = number
  default     = 7
}

# ---------------------------------------------------------
# EKS
# ---------------------------------------------------------

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "rag-chatbot-eks"
}

variable "kubernetes_version" {
  description = "Kubernetes version for EKS"
  type        = string
  default     = "1.33"
}

variable "eks_node_instance_type" {
  description = "EC2 instance type for EKS worker nodes"
  type        = string
  default     = "t3.medium"
}

variable "eks_node_count" {
  description = "Desired number of EKS worker nodes"
  type        = number
  default     = 2
}

variable "eks_autoscaler_min" {
  description = "Minimum number of EKS worker nodes"
  type        = number
  default     = 1
}

variable "eks_autoscaler_max" {
  description = "Maximum number of EKS worker nodes"
  type        = number
  default     = 3
}