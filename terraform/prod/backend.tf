terraform {
  required_version = ">= 1.5.0"

  backend "s3" {
    bucket       = "ai-kubernetes-troubleshooting-rag"
    key          = "prod/terraform.tfstate"
    region       = "ap-northeast-2"
    encrypt      = true
    use_lockfile = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}