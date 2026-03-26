"""Repository for the Review aggregate."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from los_classificados.db.models import Review
from los_classificados.data.repositories.base import Repository


class ReviewRepository(Repository[Review]):
    """Read / write access for ``reviews`` table."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ── Repository interface ──────────────────────────────────────────────────

    def get(self, id: int) -> Review | None:
        return self._session.get(Review, id)

    def list(self, **filters: Any) -> list[Review]:
        q = self._session.query(Review)
        if "subject_id" in filters:
            q = q.filter(Review.subject_id == filters["subject_id"])
        if "reviewer_id" in filters:
            q = q.filter(Review.reviewer_id == filters["reviewer_id"])
        if "listing_id" in filters:
            q = q.filter(Review.listing_id == filters["listing_id"])
        return q.order_by(Review.created_at.desc()).all()

    def add(self, entity: Review) -> Review:
        self._session.add(entity)
        return self._flush(entity)

    def update(self, entity: Review) -> Review:
        merged = self._session.merge(entity)
        return self._flush(merged)

    def delete(self, id: int) -> bool:
        review = self.get(id)
        if review is None:
            return False
        self._session.delete(review)
        return True

    # ── domain queries ────────────────────────────────────────────────────────

    def get_for_subject(self, subject_id: int) -> list[Review]:
        return self.list(subject_id=subject_id)

    def average_rating(self, subject_id: int) -> float:
        """Return the mean rating for a user; 0.0 if no reviews."""
        from sqlalchemy import func
        result = (
            self._session.query(func.avg(Review.rating))
            .filter(Review.subject_id == subject_id)
            .scalar()
        )
        return float(result) if result is not None else 0.0
