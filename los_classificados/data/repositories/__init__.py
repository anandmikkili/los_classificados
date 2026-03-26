"""Repository implementations."""
from los_classificados.data.repositories.base import Repository
from los_classificados.data.repositories.user_repo import UserRepository
from los_classificados.data.repositories.listing_repo import ListingRepository
from los_classificados.data.repositories.lead_repo import LeadRepository
from los_classificados.data.repositories.review_repo import ReviewRepository
from los_classificados.data.repositories.media_repo import MediaRepository

__all__ = [
    "Repository",
    "UserRepository",
    "ListingRepository",
    "LeadRepository",
    "ReviewRepository",
    "MediaRepository",
]
