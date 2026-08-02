variable "aws_region" {
  description = "AWS region for the Terraform state bucket"
  type        = string
  default     = "ap-northeast-2"
}

variable "project_name" {
  description = "Project name used for tags"
  type        = string
  default     = "ai-kubernetes-troubleshooting-rag"
}

variable "environment" {
  description = "Deployment environment"
  type        = string
  default     = "prod"

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "terraform_state_bucket_name" {
  description = "Globally unique S3 bucket name for Terraform state"
  type        = string

  validation {
    condition     = length(var.terraform_state_bucket_name) >= 3
    error_message = "Terraform state bucket name must contain at least 3 characters."
  }
}

variable "tags" {
  description = "Common tags applied to bootstrap resources"
  type        = map(string)

  default = {
    Project     = "AI-Kubernetes-Troubleshooting-RAG"
    Environment = "prod"
    ManagedBy   = "Terraform"
    Purpose     = "Terraform-State"
  }
}