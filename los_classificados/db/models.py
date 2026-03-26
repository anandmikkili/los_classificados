from datetime import datetime
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, JSON, String, Text, Enum as SAEnum,
)
from sqlalchemy.orm import relationship
from los_classificados.db.connection import Base
import enum


# ── Enums ──────────────────────────────────────────────────────────────────

class ListingCategory(str, enum.Enum):
    REAL_ESTATE = "real_estate"
    RENTALS = "rentals"
    SERVICES = "services"
    VEHICLES = "vehicles"
    ELECTRONICS = "electronics"
    FURNITURE = "furniture"
    JOBS = "jobs"
    OTHER = "other"


class ListingStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    SOLD = "sold"
    EXPIRED = "expired"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class PlanType(str, enum.Enum):
    FREE = "free"
    PRIME = "prime"
    ENTERPRISE = "enterprise"


# ── Models ─────────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(30))
    whatsapp = Column(String(30))
    password_hash = Column(String(255), nullable=False)
    plan = Column(SAEnum(PlanType), default=PlanType.FREE)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="US")
    avatar_s3_key = Column(String(500))
    lead_credits = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = relationship("Listing", back_populates="owner", cascade="all, delete-orphan")
    leads_received = relationship("Lead", foreign_keys="Lead.business_id", back_populates="business")
    reviews_given = relationship("Review", foreign_keys="Review.reviewer_id", back_populates="reviewer")
    reviews_received = relationship("Review", foreign_keys="Review.subject_id", back_populates="subject")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SAEnum(ListingCategory), nullable=False)
    subcategory = Column(String(100))
    price = Column(Float)
    price_negotiable = Column(Boolean, default=False)
    price_label = Column(String(50))           # "Free", "Contact for price", etc.
    city = Column(String(100))
    state = Column(String(100))
    neighborhood = Column(String(150))
    latitude = Column(Float)
    longitude = Column(Float)
    image_s3_keys = Column(JSON, default=list)   # list of S3 object keys
    attributes = Column(JSON, default=dict)      # category-specific extra fields
    status = Column(SAEnum(ListingStatus), default=ListingStatus.ACTIVE)
    is_prime_boosted = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    contact_phone = Column(String(30))
    contact_whatsapp = Column(String(30))
    contact_email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)

    owner = relationship("User", back_populates="listings")
    leads = relationship("Lead", back_populates="listing", cascade="all, delete-orphan")


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=False)
    business_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    requester_name = Column(String(120))
    requester_phone = Column(String(30))
    requester_email = Column(String(255))
    message = Column(Text)
    contact_method = Column(String(30))    # "whatsapp" | "call" | "email"
    status = Column(SAEnum(LeadStatus), default=LeadStatus.NEW)
    city = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listing = relationship("Listing", back_populates="leads")
    business = relationship("User", foreign_keys=[business_id], back_populates="leads_received")


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"))
    rating = Column(Integer, nullable=False)   # 1–5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="reviews_given")
    subject = relationship("User", foreign_keys=[subject_id], back_populates="reviews_received")
