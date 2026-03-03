from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class RecommendationStatus(str, enum.Enum):
    PENDING = "pending"
    GENERATED = "generated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=True)
    
    # Recommendation context
    occasion = Column(String, nullable=True)
    weather_temperature = Column(Float, nullable=True)
    weather_condition = Column(String, nullable=True)
    location = Column(String, nullable=True)
    
    # User preferences used
    body_type_used = Column(String, nullable=True)
    skin_tone_used = Column(String, nullable=True)
    color_preferences_used = Column(JSON, nullable=True)
    budget_range_used = Column(JSON, nullable=True)
    
    # Scores
    confidence_score = Column(Float, default=0.0)
    body_type_match_score = Column(Float, nullable=True)
    color_match_score = Column(Float, nullable=True)
    style_match_score = Column(Float, nullable=True)
    trend_relevance_score = Column(Float, nullable=True)
    
    # Status
    status = Column(SQLEnum(RecommendationStatus), default=RecommendationStatus.PENDING)
    
    # Alternative suggestions
    alternative_outfit_ids = Column(JSON, nullable=True)  # Array of outfit IDs
    
    # Duplicate detection
    is_duplicate = Column(Boolean, default=False)
    similar_outfit_ids = Column(JSON, nullable=True)
    
    # Seasonal rotation
    seasonal_tag = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="recommendations")
    outfit = relationship("Outfit")


class RecommendationRule(Base):
    __tablename__ = "recommendation_rules"

    id = Column(Integer, primary_key=True, index=True)
    
    # Rule configuration
    rule_name = Column(String, unique=True, nullable=False)
    rule_type = Column(String, nullable=False)  # body_type, color, season, occasion, etc.
    rule_config = Column(JSON, nullable=False)  # Flexible JSON configuration
    
    # Priority and weight
    priority = Column(Integer, default=0)
    weight = Column(Float, default=1.0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrendAnalysis(Base):
    __tablename__ = "trend_analysis"

    id = Column(Integer, primary_key=True, index=True)
    
    # Trend details
    trend_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Trend data
    trend_data = Column(JSON, nullable=False)  # Colors, styles, patterns, etc.
    popularity_score = Column(Float, default=0.0)
    forecast_period = Column(String, nullable=True)  # current, next_season, etc.
    
    # Source
    source = Column(String, nullable=True)  # API, manual, etc.
    source_url = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
