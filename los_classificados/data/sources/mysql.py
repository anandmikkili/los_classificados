"""MySQL data source with context-manager support and session factory."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from los_classificados.config import Config
from los_classificados.data.sources.base import DataSource

log = logging.getLogger(__name__)


class MySQLDataSource(DataSource):
    """
    Thread-safe MySQL connection pool wrapped in a context manager.

    Usage
    -----
    ::

        with MySQLDataSource() as db:
            with db.session() as session:
                listings = session.query(Listing).all()

        # or re-use a long-lived instance (e.g. app-scoped singleton)
        db = MySQLDataSource()
        db.connect()
        ...
        db.disconnect()
    """

    def __init__(
        self,
        url: str | None = None,
        *,
        pool_size: int = 10,
        max_overflow: int = 20,
        pool_recycle: int = 3600,
        echo: bool = False,
    ) -> None:
        super().__init__()
        self._url = url or Config.DATABASE_URL
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._pool_recycle = pool_recycle
        self._echo = echo

        self._engine: Engine | None = None
        self._session_factory: sessionmaker | None = None

    # ── DataSource interface ─────────────────────────────────────────────────

    def connect(self) -> None:
        if self._connected:
            return
        self._engine = create_engine(
            self._url,
            pool_pre_ping=True,
            pool_recycle=self._pool_recycle,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            echo=self._echo,
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        # validate connectivity eagerly
        with self._engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        self._connected = True
        log.info("[MySQL] Connected – pool_size=%d", self._pool_size)

    def disconnect(self) -> None:
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
            self._session_factory = None
        self._connected = False
        log.info("[MySQL] Disconnected – pool disposed")

    # ── session factory ──────────────────────────────────────────────────────

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """
        Yield a SQLAlchemy session that auto-commits on clean exit
        and rolls back on any exception.

        ::

            with db.session() as s:
                s.add(user)
        """
        if not self._connected or self._session_factory is None:
            raise RuntimeError("MySQLDataSource is not connected. Use it as a context manager.")
        sess: Session = self._session_factory()
        try:
            yield sess
            sess.commit()
        except Exception:
            sess.rollback()
            raise
        finally:
            sess.close()

    # ── health check ─────────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Return True if the database is reachable."""
        try:
            if self._engine is None:
                return False
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False
