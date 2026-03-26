"""Abstract generic repository – the backbone of the data access layer."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")  # ORM model type


class Repository(ABC, Generic[T]):
    """
    Generic CRUD contract for a single aggregate root.

    Every concrete repository receives a live SQLAlchemy ``Session`` at
    construction time.  The ``UnitOfWork`` is responsible for providing
    that session and committing / rolling back as needed.

    Pattern: Repository  (Evans, DDD)
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── mandatory interface ───────────────────────────────────────────────────

    @abstractmethod
    def get(self, id: int) -> T | None:
        """Fetch a single entity by primary key; None if not found."""

    @abstractmethod
    def list(self, **filters: Any) -> list[T]:
        """Return a (filtered) list of entities."""

    @abstractmethod
    def add(self, entity: T) -> T:
        """Persist a new entity and return it (with id populated)."""

    @abstractmethod
    def update(self, entity: T) -> T:
        """Merge changes for an existing entity and return it."""

    @abstractmethod
    def delete(self, id: int) -> bool:
        """Remove an entity by primary key; return True if found and removed."""

    # ── shared helpers ────────────────────────────────────────────────────────

    def _flush(self, entity: T) -> T:
        """Flush the session so DB-generated fields (ids, defaults) are populated."""
        self._session.flush()
        self._session.refresh(entity)
        return entity
