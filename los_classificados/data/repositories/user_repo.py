"""Repository for the User aggregate."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from los_classificados.db.models import PlanType, User
from los_classificados.data.repositories.base import Repository


class UserRepository(Repository[User]):
    """Read / write access for ``users`` table."""

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    # ── Repository interface ──────────────────────────────────────────────────

    def get(self, id: int) -> User | None:
        return self._session.get(User, id)

    def list(self, **filters: Any) -> list[User]:
        q = self._session.query(User)
        if "is_active" in filters:
            q = q.filter(User.is_active == filters["is_active"])
        if "plan" in filters:
            q = q.filter(User.plan == filters["plan"])
        if "city" in filters:
            q = q.filter(User.city == filters["city"])
        return q.all()

    def add(self, entity: User) -> User:
        self._session.add(entity)
        return self._flush(entity)

    def update(self, entity: User) -> User:
        merged = self._session.merge(entity)
        return self._flush(merged)

    def delete(self, id: int) -> bool:
        user = self.get(id)
        if user is None:
            return False
        self._session.delete(user)
        return True

    # ── domain queries ────────────────────────────────────────────────────────

    def get_by_email(self, email: str) -> User | None:
        return (
            self._session.query(User)
            .filter(User.email == email.lower())
            .first()
        )

    def get_prime_users(self) -> list[User]:
        return self._session.query(User).filter(User.plan == PlanType.PRIME).all()

    def deduct_lead_credits(self, user_id: int, amount: int = 1) -> bool:
        """Atomically deduct lead credits. Returns False if insufficient balance."""
        user = self.get(user_id)
        if user is None or user.lead_credits < amount:
            return False
        user.lead_credits -= amount
        return True
