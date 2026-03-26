"""AWS S3 utilities for image/media storage."""
import io
import uuid
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from los_classificados.config import Config


def _get_client():
    return boto3.client(
        "s3",
        region_name=Config.AWS_REGION,
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    )


def upload_image(file_bytes: bytes, content_type: str, folder: str = "listings") -> str | None:
    """Upload image bytes to S3. Returns the S3 object key or None on failure."""
    ext = content_type.split("/")[-1].replace("jpeg", "jpg")
    key = f"{folder}/{uuid.uuid4().hex}.{ext}"
    try:
        client = _get_client()
        client.put_object(
            Bucket=Config.S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
            ACL="public-read",
        )
        return key
    except (ClientError, NoCredentialsError):
        return None


def delete_image(key: str) -> bool:
    """Delete an object from S3 by key."""
    try:
        client = _get_client()
        client.delete_object(Bucket=Config.S3_BUCKET, Key=key)
        return True
    except (ClientError, NoCredentialsError):
        return False


def generate_presigned_url(key: str, expires: int = 3600) -> str:
    """Generate a temporary signed URL for a private object."""
    try:
        client = _get_client()
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": Config.S3_BUCKET, "Key": key},
            ExpiresIn=expires,
        )
    except (ClientError, NoCredentialsError):
        return ""


def public_url(key: str) -> str:
    """Return the public CDN URL for a public-read object."""
    return f"{Config.S3_BASE_URL}/{key}"
