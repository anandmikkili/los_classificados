"""
app.data – unified data API layer
==================================

Provides two app-scoped singleton sources and a ``get_uow()`` factory that
yields a ready-to-use ``UnitOfWork`` per request / operation.

Quick-start
-----------
::

    # In app startup (e.g. app/server.py or main.py):
    from los_classificados.data import data_layer
    data_layer.init()

    # In a callback / service:
    from los_classificados.data import get_uow
    with get_uow() as uow:
        listing = uow.listings.get(42)
        uow.listings.increment_views(42)
"""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from los_classificados.data.sources.mysql import MySQLDataSource
from los_classificados.data.sources.s3 import S3DataSource
from los_classificados.data.unit_of_work import UnitOfWork

log = logging.getLogger(__name__)


class DataLayer:
    """
    App-scoped singleton that holds the long-lived data source connections.

    Call ``init()`` once at application startup; call ``shutdown()`` at
    application teardown (or register it as an ``atexit`` handler).
    """

    def __init__(self) -> None:
        self.mysql: MySQLDataSource | None = None
        self.s3: S3DataSource | None = None
        self._ready = False

    def init(
        self,
        *,
        mysql: MySQLDataSource | None = None,
        s3: S3DataSource | None = None,
    ) -> None:
        """
        Connect both data sources.

        Pass pre-configured instances to override defaults (useful in tests).
        """
        self.mysql = mysql or MySQLDataSource()
        self.s3 = s3 or S3DataSource()

        try:
            self.mysql.connect()
        except Exception as exc:
            log.warning("[DataLayer] MySQL unavailable – %s", exc)
            self.mysql = None

        try:
            self.s3.connect()
        except Exception as exc:
            log.warning("[DataLayer] S3 unavailable – %s", exc)
            self.s3 = None

        self._ready = True
        log.info(
            "[DataLayer] Initialised | MySQL=%s | S3=%s",
            "ok" if self.mysql else "unavailable",
            "ok" if self.s3 else "unavailable",
        )

    def shutdown(self) -> None:
        """Dispose all data source connections."""
        if self.mysql:
            self.mysql.disconnect()
        if self.s3:
            self.s3.disconnect()
        self._ready = False
        log.info("[DataLayer] Shutdown complete")

    @property
    def is_ready(self) -> bool:
        return self._ready

    @property
    def db_available(self) -> bool:
        return self.mysql is not None and self.mysql.is_connected

    @property
    def s3_available(self) -> bool:
        return self.s3 is not None and self.s3.is_connected


# ── App-scoped singleton ──────────────────────────────────────────────────────

data_layer = DataLayer()


# ── Convenience factory ───────────────────────────────────────────────────────

@contextmanager
def get_uow() -> Generator[UnitOfWork, None, None]:
    """
    Context manager that yields a ``UnitOfWork`` backed by the app-scoped
    singletons.  Raises ``RuntimeError`` if the data layer is not initialised.

    ::

        with get_uow() as uow:
            uow.listings.add(listing)
    """
    if not data_layer.is_ready:
        raise RuntimeError("DataLayer is not initialised. Call data_layer.init() at startup.")
    if data_layer.mysql is None:
        raise RuntimeError("MySQL is not available.")
    with UnitOfWork(data_layer.mysql, data_layer.s3) as uow:
        yield uow


__all__ = [
    "DataLayer",
    "data_layer",
    "get_uow",
    "MySQLDataSource",
    "S3DataSource",
    "UnitOfWork",
]
