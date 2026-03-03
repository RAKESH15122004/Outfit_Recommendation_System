from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class ItemCategory(str, enum.Enum):
    TOP = "top"
    BOTTOM = "bottom"
    FOOTWEAR = "footwear"
    ACCESSORY = "accessory"
    OUTERWEAR = "outerwear"
    DRESS = "dress"


class ItemSubcategory(str, enum.Enum):
    # Tops
    T_SHIRT = "t_shirt"
    SHIRT = "shirt"
    BLOUSE = "blouse"
    SWEATER = "sweater"
    HOODIE = "hoodie"
    TANK_TOP = "tank_top"
    
    # Bottoms
    JEANS = "jeans"
    TROUSERS = "trousers"
    SHORTS = "shorts"
    SKIRT = "skirt"
    LEGGINGS = "leggings"
    
    # Footwear
    SNEAKERS = "sneakers"
    BOOTS = "boots"
    HEELS = "heels"
    FLATS = "flats"
    SANDALS = "sandals"
    
    # Accessories
    BAG = "bag"
    BELT = "belt"
    HAT = "hat"
    JEWELRY = "jewelry"
    SCARF = "scarf"
    
    # Outerwear
    JACKET = "jacket"
    COAT = "coat"
    BLAZER = "blazer"
    
    # Dresses
    CASUAL_DRESS = "casual_dress"
    FORMAL_DRESS = "formal_dress"
    PARTY_DRESS = "party_dress"


class Season(str, enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"
    ALL_SEASON = "all_season"


class WardrobeItem(Base):
    __tablename__ = "wardrobe_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Item details
    name = Column(String, nullable=False)
    category = Column(SQLEnum(ItemCategory), nullable=False)
    subcategory = Column(SQLEnum(ItemSubcategory), nullable=True)
    brand = Column(String, nullable=True)
    color = Column(String, nullable=False)
    size = Column(String, nullable=True)
    material = Column(String, nullable=True)
    season = Column(SQLEnum(Season), default=Season.ALL_SEASON)
    
    # Images
    image_url = Column(String, nullable=False)
    thumbnail_url = Column(String, nullable=True)
    
    # Metadata
    purchase_date = Column(DateTime, nullable=True)
    purchase_price = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)  # Array of tags
    notes = Column(Text, nullable=True)
    
    # Status
    is_available = Column(Boolean, default=True)
    is_favorite = Column(Boolean, default=False)
    wear_count = Column(Integer, default=0)
    last_worn = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="wardrobe_items")
    outfit_items = relationship("OutfitItem", back_populates="wardrobe_item", cascade="all, delete-orphan")


class WardrobeCategory(Base):
    __tablename__ = "wardrobe_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
