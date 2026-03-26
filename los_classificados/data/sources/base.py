"""Abstract base for all data source connections."""
from __future__ import annotations

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self


class DataSource(ABC):
    """
    Protocol for any data source (database, object store, cache, …).

    Subclasses must implement ``connect`` and ``disconnect``; the context
    manager protocol is provided here for free.
    """

    _connected: bool = False

    # ── lifecycle ────────────────────────────────────────────────────────────

    @abstractmethod
    def connect(self) -> None:
        """Open / initialise the underlying connection or pool."""

    @abstractmethod
    def disconnect(self) -> None:
        """Release / close the underlying connection or pool."""

    @property
    def is_connected(self) -> bool:
        return self._connected

    # ── context manager ──────────────────────────────────────────────────────

    def __enter__(self) -> Self:
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> bool:
        self.disconnect()
        return False  # never suppress exceptions
