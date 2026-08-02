AI Kubernetes Troubleshooting RAG Platform

A production-style AI platform that analyzes Kubernetes failure logs and troubleshooting documents, retrieves relevant evidence using PostgreSQL with pgvector, and generates structured incident reports with recommended kubectl commands and remediation steps.

Project status

Core platform: complete and operational

Infrastructure provisioned with Terraform

Application deployed to Amazon EKS

Documents stored in Amazon S3

Vector search implemented with PostgreSQL and pgvector

Conversation state stored in PostgreSQL with LangGraph checkpointing

Public access provided through AWS ALB Ingress

CI/CD implemented using GitHub Actions and AWS OIDC

Kubernetes metrics available through Metrics Server

Logs and infrastructure metrics available in CloudWatch Container Insights

What the platform solves

The assistant helps investigate incidents such as:

CrashLoopBackOff

OOMKilled

ImagePullBackOff

Container startup failures

Pod scheduling failures

Incorrect Kubernetes configuration

Missing dependencies and application runtime errors

Responses follow a production incident structure:

Incident Summary

Severity

Root Cause

Evidence from Retrieved Logs/Documents

Impact

Recommended kubectl Commands

Resolution Steps

Preventive Actions

Architecture

flowchart TD
    User[DevOps Engineer / User] --> ALB[AWS Application Load Balancer]
    ALB --> Ingress[Kubernetes Ingress]
    Ingress --> Service[ClusterIP Service]
    Service --> Pod1[RAG API Pod 1]
    Service --> Pod2[RAG API Pod 2]

    Pod1 --> OpenAI[OpenAI API]
    Pod2 --> OpenAI

    Pod1 --> RDS[(Amazon RDS PostgreSQL)]
    Pod2 --> RDS
    RDS --> VectorDB[(vectordb + pgvector)]
    RDS --> StateDB[(statedb + LangGraph checkpoints)]

    Pod1 --> S3[(Amazon S3 Documents)]
    Pod2 --> S3

    GitHub[GitHub Repository] --> Actions[GitHub Actions CI/CD]
    Actions --> ECR[Amazon ECR]
    ECR --> EKS[Amazon EKS]
    Actions --> EKS

    Terraform[Terraform] --> VPC[AWS VPC]
    Terraform --> EKS
    Terraform --> RDS
    Terraform --> S3
    Terraform --> IAM[IAM + GitHub OIDC]

    EKS --> Metrics[Metrics Server]
    EKS --> CloudWatch[CloudWatch Container Insights]

Technology stack

Area

Technology

API

FastAPI, Uvicorn

RAG

LangChain

Conversation workflow

LangGraph

LLM and embeddings

OpenAI

Vector database

Amazon RDS PostgreSQL, pgvector

State database

Amazon RDS PostgreSQL

Document storage

Amazon S3

Containerization

Docker

Registry

Amazon ECR

Kubernetes

Amazon EKS

Load balancing

AWS Load Balancer Controller, ALB Ingress

Infrastructure as Code

Terraform

CI/CD

GitHub Actions

AWS authentication

GitHub OIDC, IAM roles

Monitoring

Metrics Server, CloudWatch Container Insights

Logging

Fluent Bit, CloudWatch Logs

Repository structure

.
├── .github/
│   └── workflows/
│       └── deploy.yaml
├── app/
│   ├── api/
│   ├── core/
│   ├── static/
│   └── main.py
├── k8s/
│   ├── namespace.yaml
│   ├── service-account.yaml
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── db-init-job.yaml
├── terraform/
│   ├── bootstrap/
│   └── prod/
├── Dockerfile
├── requirements.txt
└── README.md

Deployment process

1. Run locally

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000/docs
http://127.0.0.1:8000/api/health

2. Build the Docker image

docker build -t ai-kubernetes-troubleshooting-rag:v1 .

3. Push to Amazon ECR

$REGION = "ap-northeast-2"
$ACCOUNT_ID = aws sts get-caller-identity --query Account --output text
$REPOSITORY = "ai-kubernetes-troubleshooting-rag"
$IMAGE_URI = "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${REPOSITORY}:v1.0.0"

aws ecr get-login-password --region $REGION |
docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"

docker tag ai-kubernetes-troubleshooting-rag:v1 $IMAGE_URI
docker push $IMAGE_URI

4. Create Terraform remote state

cd terraform\bootstrap
terraform init
terraform validate
terraform plan
terraform apply

5. Provision AWS infrastructure

cd ..\prod
terraform init
terraform fmt
terraform validate
terraform plan
terraform apply

Terraform provisions:

Custom VPC

Public and private subnets

Internet Gateway and NAT Gateway

Route tables

Security groups

Amazon RDS PostgreSQL

Amazon S3 document bucket

Amazon EKS and managed node group

IAM roles and EKS add-ons

GitHub OIDC deployment role

CloudWatch observability add-on

6. Connect to EKS

aws eks update-kubeconfig `
  --region ap-northeast-2 `
  --name ai-k8s-rag-prod

kubectl get nodes

7. Initialize the databases

The database initialization Job:

Validates RDS connectivity

Enables pgvector

Creates statedb

kubectl apply -f k8s\db-init-job.yaml
kubectl logs job/rag-db-init -n rag-production

8. Deploy the application

kubectl apply -f k8s\namespace.yaml
kubectl apply -f k8s\service-account.yaml
kubectl apply -f k8s\configmap.yaml
kubectl apply -f k8s\deployment.yaml
kubectl apply -f k8s\service.yaml
kubectl apply -f k8s\ingress.yaml

Verify:

kubectl get pods -n rag-production
kubectl get service -n rag-production
kubectl get ingress -n rag-production
kubectl rollout status deployment/rag-api -n rag-production

CI/CD

Every push to main triggers the GitHub Actions pipeline:

Git push
  ↓
GitHub Actions requests an OIDC token
  ↓
AWS IAM role is assumed
  ↓
Docker image is built
  ↓
Image is pushed to Amazon ECR with the commit SHA
  ↓
EKS kubeconfig is generated
  ↓
Kubernetes Deployment image is updated
  ↓
Rolling rollout is verified

No permanent AWS access keys are stored in GitHub.

API documentation

Swagger UI:

http://<ALB-DNS>/docs

Health check

GET /api/health

Example response:

{
  "status": "healthy",
  "vector_db": "connected",
  "state_db": "connected",
  "openai_api": "available"
}

Start document indexing

POST /api/admin/index_documents

Required header:

x-api-key: <ADMIN_API_KEY>

Example response:

{
  "success": true,
  "job_id": "a4683215-5d55-423b-a04a-37c5241d47bb",
  "status": "queued",
  "message": "Indexing started in background."
}

Check indexing status

GET /api/admin/index_documents/{job_id}

Required header:

x-api-key: <ADMIN_API_KEY>

Example response:

{
  "job_id": "a4683215-5d55-423b-a04a-37c5241d47bb",
  "status": "completed",
  "result": {
    "documents_processed": 2,
    "chunks_created": 48,
    "failed_documents": []
  },
  "error": null
}

Chat endpoint

Confirm the exact chat route and request schema in Swagger UI because the final repository implementation controls the route name.

Example question:

Analyze the CrashLoopBackOff incident from the uploaded logs and generate a structured production incident report.

Expected answer format:

1. Incident Summary
2. Severity
3. Root Cause
4. Evidence from Retrieved Logs/Documents
5. Impact
6. Recommended kubectl Commands
7. Resolution Steps
8. Preventive Actions

Example test questions

Analyze the CrashLoopBackOff incident from the uploaded logs and generate a structured production incident report.

Compare CrashLoopBackOff, OOMKilled, and ImagePullBackOff using evidence from the indexed documents.

Which kubectl command should be used to retrieve logs from the previous crashed container, and why?

What is the exact database password used by the failed pod?

For the final question, the expected behavior is to state that the retrieved documents do not contain that information.

Monitoring and logging

Kubernetes metrics:

kubectl top nodes
kubectl top pods -n rag-production

CloudWatch log groups:

/aws/containerinsights/ai-k8s-rag-prod/application
/aws/containerinsights/ai-k8s-rag-prod/dataplane
/aws/containerinsights/ai-k8s-rag-prod/host

Screenshots

Swagger UI

<img width="975" height="522" alt="image" src="https://github.com/user-attachments/assets/f97f221a-550f-4249-a9ea-693c533e0e36" />


Health API
<img width="1355" height="688" alt="image" src="https://github.com/user-attachments/assets/6c74ba45-e6c7-4701-9fd2-ea3e886a5026" />



Screenshots still recommended

Add these under docs/screenshots/:

01-architecture.png
04-rag-incident-response.png
05-eks-nodes.png
06-kubernetes-pods.png
07-github-actions-success.png
08-ecr-image.png
09-alb-ingress.png
10-cloudwatch-container-insights.png
11-terraform-apply.png

Do not expose API keys, AWS access keys, database passwords, Kubernetes Secret values, or full connection strings in screenshots.

Security design

EKS worker nodes run in private subnets.

RDS runs in private database subnets.

PostgreSQL port 5432 is restricted to the EKS cluster security group.

S3 public access is blocked.

Terraform state is encrypted and versioned.

GitHub Actions uses OIDC instead of long-lived credentials.

EKS Pod Identity provides AWS access to workloads.

Kubernetes readiness and liveness probes protect availability.

ALB sends traffic only to healthy targets.

Troubleshooting

Pod failure

kubectl get pods -n rag-production
kubectl describe pod <pod-name> -n rag-production
kubectl logs <pod-name> -n rag-production
kubectl logs <pod-name> -n rag-production --previous

Service has no endpoints

kubectl get endpoints rag-api-service -n rag-production
kubectl get pods -n rag-production --show-labels

Ingress issue

kubectl describe ingress rag-api-ingress -n rag-production
kubectl logs deployment/aws-load-balancer-controller -n kube-system

Database connectivity issue

kubectl logs deployment/rag-api -n rag-production

Cleanup and cost control

The following resources continue generating charges while active:

Amazon EKS

EC2 worker nodes

NAT Gateway

Application Load Balancer

Amazon RDS

CloudWatch logs and metrics

To remove the Kubernetes workloads:

kubectl delete -f k8s\ingress.yaml
kubectl delete -f k8s\service.yaml
kubectl delete -f k8s\deployment.yaml
kubectl delete -f k8s\configmap.yaml
kubectl delete -f k8s\service-account.yaml
kubectl delete -f k8s\namespace.yaml

Then destroy the infrastructure:

cd terraform\prod
terraform destroy
