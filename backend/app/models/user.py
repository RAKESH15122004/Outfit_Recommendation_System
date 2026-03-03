from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    
    # User preferences
    body_type = Column(String, nullable=True)  # petite, athletic, curvy, tall, etc.
    skin_tone = Column(String, nullable=True)  # warm, cool, neutral
    preferred_colors = Column(String, nullable=True)  # JSON array
    brand_affinity = Column(String, nullable=True)  # JSON array
    comfort_level = Column(String, nullable=True)  # casual, moderate, formal
    budget_range = Column(String, nullable=True)  # JSON: {"min": 0, "max": 1000}
    
    # Profile
    profile_image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    wardrobe_items = relationship("WardrobeItem", back_populates="owner", cascade="all, delete-orphan")
    outfits = relationship("Outfit", back_populates="user", cascade="all, delete-orphan")
    saved_outfits = relationship("SavedOutfit", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="user", cascade="all, delete-orphan")
