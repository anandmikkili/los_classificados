"""Repository for the Lead aggregate."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from los_classificados.db.models import Lead, LeadStatus
from los_classificados.data.repositories.base import Repository


class LeadRepository(Repository[Lead]):
    """Read / write access for ``leads`` table."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ── Repository interface ──────────────────────────────────────────────────

    def get(self, id: int) -> Lead | None:
        return self._session.get(Lead, id)

    def list(self, **filters: Any) -> list[Lead]:
        q = self._session.query(Lead)
        if "business_id" in filters:
            q = q.filter(Lead.business_id == filters["business_id"])
        if "listing_id" in filters:
            q = q.filter(Lead.listing_id == filters["listing_id"])
        if "status" in filters:
            q = q.filter(Lead.status == filters["status"])
        return q.order_by(Lead.created_at.desc()).all()

    def add(self, entity: Lead) -> Lead:
        self._session.add(entity)
        return self._flush(entity)

    def update(self, entity: Lead) -> Lead:
        merged = self._session.merge(entity)
        return self._flush(merged)

    def delete(self, id: int) -> bool:
        lead = self.get(id)
        if lead is None:
            return False
        self._session.delete(lead)
        return True

    # ── domain queries ────────────────────────────────────────────────────────

    def get_for_business(self, business_id: int, status: LeadStatus | None = None) -> list[Lead]:
        filters: dict[str, Any] = {"business_id": business_id}
        if status:
            filters["status"] = status
        return self.list(**filters)

    def update_status(self, lead_id: int, status: LeadStatus) -> Lead | None:
        lead = self.get(lead_id)
        if lead:
            lead.status = status
        return lead

    def count_for_listing(self, listing_id: int) -> int:
        return (
            self._session.query(Lead)
            .filter(Lead.listing_id == listing_id)
            .count()
        )
