from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class OutfitCategory(str, enum.Enum):
    CASUAL_WEAR = "casual_wear"
    FORMAL_WEAR = "formal_wear"
    OCCASION_WEAR = "occasion_wear"


class OccasionType(str, enum.Enum):
    DAILY = "daily"
    STREET_STYLE = "street_style"
    SMART_CASUAL = "smart_casual"
    OFFICE = "office"
    BUSINESS_MEETING = "business_meeting"
    CORPORATE_EVENT = "corporate_event"
    WEDDING = "wedding"
    PARTY = "party"
    FESTIVAL = "festival"
    SPECIAL_EVENT = "special_event"


class Outfit(Base):
    __tablename__ = "outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Outfit details
    name = Column(String, nullable=True)
    category = Column(SQLEnum(OutfitCategory), nullable=False)
    occasion = Column(SQLEnum(OccasionType), nullable=True)
    
    # AI-generated metadata
    confidence_score = Column(Float, default=0.0)  # 0.0 to 1.0
    color_coordination_score = Column(Float, nullable=True)
    style_match_score = Column(Float, nullable=True)
    weather_appropriateness = Column(Float, nullable=True)
    
    # Weather context
    weather_temperature = Column(Float, nullable=True)
    weather_condition = Column(String, nullable=True)  # sunny, rainy, cold, etc.
    weather_location = Column(String, nullable=True)
    
    # Styling preferences used
    dress_code = Column(String, nullable=True)
    color_preferences = Column(JSON, nullable=True)
    brand_preferences = Column(JSON, nullable=True)
    
    # Preview
    preview_image_url = Column(String, nullable=True)
    is_ai_generated = Column(Boolean, default=True)
    
    # Status
    is_saved = Column(Boolean, default=False)
    is_favorite = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    worn_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="outfits")
    items = relationship("OutfitItem", back_populates="outfit", cascade="all, delete-orphan")
    history = relationship("OutfitHistory", back_populates="outfit", cascade="all, delete-orphan")


class OutfitItem(Base):
    __tablename__ = "outfit_items"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    wardrobe_item_id = Column(Integer, ForeignKey("wardrobe_items.id"), nullable=True)
    
    # Item details (can be stored even if wardrobe_item is deleted)
    item_type = Column(String, nullable=False)  # top, bottom, footwear, accessory
    item_name = Column(String, nullable=True)
    item_color = Column(String, nullable=True)
    item_image_url = Column(String, nullable=True)
    
    # Position/order in outfit
    display_order = Column(Integer, default=0)
    
    # Relationships
    outfit = relationship("Outfit", back_populates="items")
    wardrobe_item = relationship("WardrobeItem", back_populates="outfit_items")


class OutfitHistory(Base):
    __tablename__ = "outfit_history"

    id = Column(Integer, primary_key=True, index=True)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Event details
    event_name = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=True)
    event_location = Column(String, nullable=True)
    
    # Feedback
    user_feedback = Column(Text, nullable=True)
    rating = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    outfit = relationship("Outfit", back_populates="history")


class SavedOutfit(Base):
    __tablename__ = "saved_outfits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    outfit_id = Column(Integer, ForeignKey("outfits.id"), nullable=False)
    
    # Custom name/notes
    custom_name = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Reminder settings
    reminder_date = Column(DateTime, nullable=True)
    reminder_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_outfits")
    outfit = relationship("Outfit")
