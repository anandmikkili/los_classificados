"""S3-backed media repository for listing images and user avatars."""
from __future__ import annotations

import logging
from typing import IO

from los_classificados.data.sources.s3 import S3DataSource

log = logging.getLogger(__name__)


class MediaRepository:
    """
    High-level media operations built on top of ``S3DataSource``.

    Unlike the SQL repositories this class is **not** generic – it owns its
    own interface because object-store semantics differ from relational ones
    (no primary keys, bulk deletes, signed URLs, etc.).

    The ``S3DataSource`` is injected (never created here) so the caller
    controls the connection lifecycle.
    """

    def __init__(self, s3: S3DataSource) -> None:
        self._s3 = s3

    # ── write ─────────────────────────────────────────────────────────────────

    def upload_listing_image(
        self,
        data: bytes | IO[bytes],
        content_type: str,
        listing_id: int | None = None,
    ) -> str:
        """
        Upload a listing image; returns the S3 object key.

        Keys are namespaced under ``listings/<uuid>.<ext>`` so that objects
        can be bulk-deleted when a listing is removed.
        """
        folder = f"listings/{listing_id}" if listing_id else "listings"
        return self._s3.upload(data, content_type, folder=folder)

    def upload_avatar(self, data: bytes | IO[bytes], content_type: str, user_id: int) -> str:
        """Upload a user avatar; returns the S3 key."""
        return self._s3.upload(data, content_type, folder=f"avatars/{user_id}")

    # ── read ──────────────────────────────────────────────────────────────────

    def download(self, key: str) -> bytes:
        """Download raw bytes for *key*."""
        return self._s3.download(key)

    def public_url(self, key: str) -> str:
        """Return the public CDN URL for a public-read object."""
        return self._s3.public_url(key)

    def presigned_url(self, key: str, expires: int = 3600) -> str:
        """Return a temporary signed URL for a private object."""
        return self._s3.presigned_url(key, expires=expires)

    def exists(self, key: str) -> bool:
        return self._s3.exists(key)

    # ── delete ────────────────────────────────────────────────────────────────

    def delete(self, key: str) -> bool:
        return self._s3.delete(key)

    def delete_listing_images(self, keys: list[str]) -> int:
        """Batch-delete all images for a listing. Returns count deleted."""
        return self._s3.delete_many(keys)

    # ── listing helpers ───────────────────────────────────────────────────────

    def listing_image_urls(self, keys: list[str]) -> list[str]:
        """Resolve a list of S3 keys to their public URLs."""
        return [self._s3.public_url(k) for k in keys if k]
