"""
Unit of Work pattern
====================

``UnitOfWork`` coordinates a MySQL session and (optionally) the S3 client
so that all repository operations within a single ``with`` block share one
session and are committed or rolled back atomically.

Pattern: Unit of Work  (Fowler, P of EAA)

Usage
-----
::

    # App-scoped singletons (created once at startup)
    mysql = MySQLDataSource()
    mysql.connect()

    s3 = S3DataSource()
    s3.connect()

    # Per-request scope
    with UnitOfWork(mysql, s3) as uow:
        listing = Listing(title="Casa en Bogotá", ...)
        uow.listings.add(listing)

        key = uow.media.upload_listing_image(img_bytes, "image/jpeg", listing.id)
        listing.image_s3_keys = [key]

    # commit() is called automatically on clean __exit__
    # rollback() is called automatically on exception

    # S3 cannot be rolled back, but uow.pending_s3_deletes lets you clean up
    # if the DB commit fails (see _compensate_s3).
"""
from __future__ import annotations

import logging
from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session

from los_classificados.data.repositories.lead_repo import LeadRepository
from los_classificados.data.repositories.listing_repo import ListingRepository
from los_classificados.data.repositories.media_repo import MediaRepository
from los_classificados.data.repositories.review_repo import ReviewRepository
from los_classificados.data.repositories.user_repo import UserRepository
from los_classificados.data.sources.mysql import MySQLDataSource
from los_classificados.data.sources.s3 import S3DataSource

log = logging.getLogger(__name__)


class UnitOfWork:
    """
    Transactional scope that exposes all repositories as attributes.

    Parameters
    ----------
    mysql:
        A **connected** ``MySQLDataSource`` instance.  Typically a
        singleton shared across requests (connection pool).
    s3:
        A **connected** ``S3DataSource`` instance.  Optional; if omitted,
        ``self.media`` is unavailable.
    """

    def __init__(
        self,
        mysql: MySQLDataSource,
        s3: S3DataSource | None = None,
    ) -> None:
        self._mysql = mysql
        self._s3 = s3

        self._session: Session | None = None
        self._session_ctx = None

        # S3 keys uploaded in this UoW – used for compensation on DB failure
        self._uploaded_keys: list[str] = []

    # ── context manager ───────────────────────────────────────────────────────

    def __enter__(self) -> Self:
        self._session_ctx = self._mysql.session()
        self._session = self._session_ctx.__enter__()
        self._init_repositories()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        if exc_type is not None:
            # DB session will be rolled back by MySQLDataSource.session()
            log.warning("[UoW] Rolling back – %s: %s", exc_type.__name__, exc_val)
            self._compensate_s3()
        # Delegate commit/rollback to the session context manager
        self._session_ctx.__exit__(exc_type, exc_val, exc_tb)
        self._session = None
        return False

    # ── repository access ─────────────────────────────────────────────────────

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def listings(self) -> ListingRepository:
        return self._listings

    @property
    def leads(self) -> LeadRepository:
        return self._leads

    @property
    def reviews(self) -> ReviewRepository:
        return self._reviews

    @property
    def media(self) -> MediaRepository:
        if self._s3 is None:
            raise RuntimeError("UnitOfWork was created without an S3DataSource.")
        return self._media

    # ── explicit control (advanced) ──────────────────────────────────────────

    def commit(self) -> None:
        """Flush + commit the current session immediately (rarely needed)."""
        if self._session:
            self._session.commit()
            self._uploaded_keys.clear()

    def rollback(self) -> None:
        """Explicit rollback + S3 compensation."""
        if self._session:
            self._session.rollback()
        self._compensate_s3()

    # ── internals ────────────────────────────────────────────────────────────

    def _init_repositories(self) -> None:
        assert self._session is not None
        self._users = UserRepository(self._session)
        self._listings = ListingRepository(self._session)
        self._leads = LeadRepository(self._session)
        self._reviews = ReviewRepository(self._session)
        if self._s3 is not None:
            # Wrap MediaRepository so we track uploaded keys for compensation
            self._media = _TrackingMediaRepository(self._s3, self._uploaded_keys)

    def _compensate_s3(self) -> None:
        """Best-effort delete of S3 objects uploaded during a failed transaction."""
        if self._s3 and self._uploaded_keys:
            count = self._s3.delete_many(list(self._uploaded_keys))
            log.info("[UoW] S3 compensation deleted %d object(s)", count)
            self._uploaded_keys.clear()


class _TrackingMediaRepository(MediaRepository):
    """MediaRepository that records every uploaded key for UoW compensation."""

    def __init__(self, s3: S3DataSource, tracker: list[str]) -> None:
        super().__init__(s3)
        self._tracker = tracker

    def upload_listing_image(self, data, content_type, listing_id=None) -> str:
        key = super().upload_listing_image(data, content_type, listing_id)
        self._tracker.append(key)
        return key

    def upload_avatar(self, data, content_type, user_id) -> str:
        key = super().upload_avatar(data, content_type, user_id)
        self._tracker.append(key)
        return key
