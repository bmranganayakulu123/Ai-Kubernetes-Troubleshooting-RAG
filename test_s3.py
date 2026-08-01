import boto3
from app.core.config import get_settings

settings = get_settings()

s3 = boto3.client(
    "s3",
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key
)

response = s3.list_objects_v2(
    Bucket=settings.aws_s3_bucket
)

print("S3 connection successful")
print("Bucket:", settings.aws_s3_bucket)
print("Objects:", response.get("Contents", []))