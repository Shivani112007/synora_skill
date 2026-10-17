import boto3

from app import AWS_REGION, S3_BUCKET


def get_s3():
    if not S3_BUCKET:
        raise RuntimeError("S3_BUCKET is not configured.")
    return boto3.client(
        "s3",
        region_name=AWS_REGION,
        endpoint_url=f"https://s3.{AWS_REGION}.amazonaws.com",
    )


def get_user_documents(u):

    return u.setdefault("documents", [])
