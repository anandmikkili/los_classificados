"""Repository for the Listing aggregate."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from los_classificados.db.models import Listing, ListingCategory, ListingStatus
from los_classificados.data.repositories.base import Repository


class ListingRepository(Repository[Listing]):
    """Read / write access for ``listings`` table."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ── Repository interface ──────────────────────────────────────────────────

    def get(self, id: int) -> Listing | None:
        return self._session.get(Listing, id)

    def list(self, **filters: Any) -> list[Listing]:
        q = self._session.query(Listing)
        if "status" in filters:
            q = q.filter(Listing.status == filters["status"])
        if "category" in filters:
            q = q.filter(Listing.category == filters["category"])
        if "owner_id" in filters:
            q = q.filter(Listing.owner_id == filters["owner_id"])
        if "city" in filters:
            q = q.filter(Listing.city == filters["city"])
        if "is_prime_boosted" in filters:
            q = q.filter(Listing.is_prime_boosted == filters["is_prime_boosted"])
        limit: int | None = filters.get("limit")
        if limit:
            q = q.limit(limit)
        return q.order_by(Listing.is_prime_boosted.desc(), Listing.created_at.desc()).all()

    def add(self, entity: Listing) -> Listing:
        self._session.add(entity)
        return self._flush(entity)

    def update(self, entity: Listing) -> Listing:
        merged = self._session.merge(entity)
        return self._flush(merged)

    def delete(self, id: int) -> bool:
        listing = self.get(id)
        if listing is None:
            return False
        self._session.delete(listing)
        return True

    # ── domain queries ────────────────────────────────────────────────────────

    def get_active(self, limit: int = 50) -> list[Listing]:
        return self.list(status=ListingStatus.ACTIVE, limit=limit)

    def get_by_category(
        self, category: ListingCategory, status: ListingStatus = ListingStatus.ACTIVE
    ) -> list[Listing]:
        return self.list(category=category, status=status)

    def get_by_owner(self, owner_id: int) -> list[Listing]:
        return self.list(owner_id=owner_id)

    def increment_views(self, listing_id: int) -> None:
        listing = self.get(listing_id)
        if listing:
            listing.views = (listing.views or 0) + 1

    def search(self, query: str, city: str | None = None, limit: int = 50) -> list[Listing]:
        """Full-text style search on title + description (LIKE-based for now)."""
        q = (
            self._session.query(Listing)
            .filter(
                Listing.status == ListingStatus.ACTIVE,
                (Listing.title.ilike(f"%{query}%") | Listing.description.ilike(f"%{query}%")),
            )
        )
        if city:
            q = q.filter(Listing.city == city)
        return q.order_by(Listing.is_prime_boosted.desc(), Listing.created_at.desc()).limit(limit).all()

    def expire_old_listings(self) -> int:
        """Mark listings whose ``expires_at`` is in the past as EXPIRED."""
        now = datetime.utcnow()
        rows = (
            self._session.query(Listing)
            .filter(
                Listing.status == ListingStatus.ACTIVE,
                Listing.expires_at <= now,
            )
            .all()
        )
        for listing in rows:
            listing.status = ListingStatus.EXPIRED
        return len(rows)
