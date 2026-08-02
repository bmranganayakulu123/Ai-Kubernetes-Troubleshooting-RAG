resource "aws_iam_role" "rag_app" {
  name = "${var.project_name}-${var.environment}-rag-app-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Principal = {
          Service = "pods.eks.amazonaws.com"
        }

        Action = [
          "sts:AssumeRole",
          "sts:TagSession"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy" "rag_app_s3" {
  name = "${var.project_name}-${var.environment}-s3-read"
  role = aws_iam_role.rag_app.id

  policy = jsonencode({
    Version = "2012-10-17"

    Statement = [
      {
        Effect = "Allow"

        Action = [
          "s3:ListBucket"
        ]

        Resource = aws_s3_bucket.documents.arn

        Condition = {
          StringLike = {
            "s3:prefix" = [
              "documents",
              "documents/*"
            ]
          }
        }
      },
      {
        Effect = "Allow"

        Action = [
          "s3:GetObject"
        ]

        Resource = "${aws_s3_bucket.documents.arn}/documents/*"
      }
    ]
  })
}

resource "aws_eks_pod_identity_association" "rag_app" {
  cluster_name    = aws_eks_cluster.main.name
  namespace       = "rag-production"
  service_account = "rag-api"
  role_arn        = aws_iam_role.rag_app.arn

  depends_on = [
    aws_eks_addon.pod_identity_agent
  ]
}