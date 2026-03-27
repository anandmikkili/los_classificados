"""AWS S3 data source with context-manager support."""
from __future__ import annotations

import io
import logging
import uuid
from typing import IO, Any

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from los_classificados.config import Config
from los_classificados.data.sources.base import DataSource

log = logging.getLogger(__name__)


class S3DataSource(DataSource):
    """
    Thin, reusable wrapper around a boto3 S3 client.

    A single boto3 client is created on ``connect`` and shared across all
    operations for the lifetime of the source.  Disposing on ``disconnect``
    is a no-op for S3 (HTTP connections are returned to urllib3's pool
    automatically), but the pattern keeps the API consistent with MySQL.

    Usage
    -----
    ::

        with S3DataSource() as s3:
            key = s3.upload(data, "image/jpeg", folder="listings")
            url = s3.public_url(key)

        # or reuse a long-lived instance
        s3 = S3DataSource()
        s3.connect()
        ...
        s3.disconnect()
    """

    def __init__(
        self,
        bucket: str | None = None,
        *,
        region: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        endpoint_url: str | None = None,      # useful for LocalStack / MinIO
    ) -> None:
        super().__init__()
        self._bucket = bucket or Config.S3_BUCKET
        self._region = region or Config.AWS_REGION
        self._access_key = access_key or Config.AWS_ACCESS_KEY_ID
        self._secret_key = secret_key or Config.AWS_SECRET_ACCESS_KEY
        self._endpoint_url = endpoint_url
        self._client: Any = None

    # ── DataSource interface ─────────────────────────────────────────────────

    def connect(self) -> None:
        if self._connected:
            return
        kwargs: dict[str, Any] = {
            "region_name": self._region,
            "aws_access_key_id": self._access_key,
            "aws_secret_access_key": self._secret_key,
        }
        if self._endpoint_url:
            kwargs["endpoint_url"] = self._endpoint_url
        self._client = boto3.client("s3", **kwargs)
        self._connected = True
        log.info("[S3] Client initialised (bucket=%s, region=%s)", self._bucket, self._region)

    def disconnect(self) -> None:
        # boto3 clients are not closeable; we just drop the reference
        self._client = None
        self._connected = False
        log.info("[S3] Client released")

    # ── write operations ─────────────────────────────────────────────────────

    def upload(
        self,
        data: bytes | IO[bytes],
        content_type: str,
        *,
        folder: str = "uploads",
        key: str | None = None,
        public: bool = True,
        metadata: dict[str, str] | None = None,
    ) -> str:
        """
        Upload bytes or a file-like object to S3.

        Returns the S3 object key.  Raises ``ClientError`` on failure.
        """
        self._require_client()
        if key is None:
            ext = content_type.split("/")[-1].replace("jpeg", "jpg")
            key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        body = data if isinstance(data, bytes) else data.read()

        put_kwargs: dict[str, Any] = {
            "Bucket": self._bucket,
            "Key": key,
            "Body": body,
            "ContentType": content_type,
        }
        if public:
            put_kwargs["ACL"] = "public-read"
        if metadata:
            put_kwargs["Metadata"] = metadata

        self._client.put_object(**put_kwargs)
        log.debug("[S3] Uploaded %s (%d bytes)", key, len(body))
        return key

    def upload_file(
        self,
        local_path: str,
        *,
        folder: str = "uploads",
        key: str | None = None,
        extra_args: dict[str, Any] | None = None,
    ) -> str:
        """Upload a local file by path using multipart transfer (large-file safe)."""
        self._require_client()
        if key is None:
            suffix = local_path.rsplit(".", 1)[-1]
            key = f"{folder}/{uuid.uuid4().hex}.{suffix}"
        self._client.upload_file(local_path, self._bucket, key, ExtraArgs=extra_args or {})
        log.debug("[S3] Uploaded file %s → %s", local_path, key)
        return key

    # ── read operations ──────────────────────────────────────────────────────

    def download(self, key: str) -> bytes:
        """Download an object and return its raw bytes.  Raises on failure."""
        self._require_client()
        response = self._client.get_object(Bucket=self._bucket, Key=key)
        data: bytes = response["Body"].read()
        log.debug("[S3] Downloaded %s (%d bytes)", key, len(data))
        return data

    def download_stream(self, key: str) -> io.BytesIO:
        """Download an object into an in-memory BytesIO stream."""
        return io.BytesIO(self.download(key))

    def object_metadata(self, key: str) -> dict[str, Any]:
        """Return S3 object metadata (head_object result)."""
        self._require_client()
        return self._client.head_object(Bucket=self._bucket, Key=key)

    def exists(self, key: str) -> bool:
        """Return True if the key exists in the bucket."""
        try:
            self.object_metadata(key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("404", "NoSuchKey"):
                return False
            raise

    def list_objects(self, prefix: str = "", max_keys: int = 1000) -> list[dict[str, Any]]:
        """Return a list of object summaries under *prefix*."""
        self._require_client()
        response = self._client.list_objects_v2(
            Bucket=self._bucket, Prefix=prefix, MaxKeys=max_keys
        )
        return response.get("Contents", [])

    # ── delete operations ────────────────────────────────────────────────────

    def delete(self, key: str) -> bool:
        """Delete a single object. Returns True on success."""
        try:
            self._require_client()
            self._client.delete_object(Bucket=self._bucket, Key=key)
            log.debug("[S3] Deleted %s", key)
            return True
        except (ClientError, NoCredentialsError) as exc:
            log.warning("[S3] delete failed for %s: %s", key, exc)
            return False

    def delete_many(self, keys: list[str]) -> int:
        """Batch-delete up to 1 000 keys. Returns count of deleted objects."""
        self._require_client()
        if not keys:
            return 0
        objects = [{"Key": k} for k in keys]
        response = self._client.delete_objects(
            Bucket=self._bucket, Delete={"Objects": objects}
        )
        deleted = len(response.get("Deleted", []))
        log.debug("[S3] Batch-deleted %d objects", deleted)
        return deleted

    # ── URL helpers ───────────────────────────────────────────────────────────

    def public_url(self, key: str) -> str:
        """Return the public HTTPS URL for a public-read object."""
        base = (
            f"{self._endpoint_url}/{self._bucket}"
            if self._endpoint_url
            else f"https://{self._bucket}.s3.amazonaws.com"
        )
        return f"{base}/{key}"

    def presigned_url(self, key: str, expires: int = 3600, operation: str = "get_object") -> str:
        """Generate a pre-signed URL for temporary access to a private object."""
        self._require_client()
        return self._client.generate_presigned_url(
            operation,
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires,
        )

    # ── health check ─────────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Return True if S3 credentials and bucket are reachable."""
        try:
            self._require_client()
            self._client.head_bucket(Bucket=self._bucket)
            return True
        except Exception:
            return False

    # ── internals ────────────────────────────────────────────────────────────

    def _require_client(self) -> None:
        if not self._connected or self._client is None:
            raise RuntimeError("S3DataSource is not connected. Use it as a context manager.")
