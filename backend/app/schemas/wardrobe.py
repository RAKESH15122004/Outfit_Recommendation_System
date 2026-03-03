from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.wardrobe import ItemCategory, ItemSubcategory, Season


class WardrobeItemBase(BaseModel):
    name: str
    category: ItemCategory
    subcategory: Optional[ItemSubcategory] = None
    brand: Optional[str] = None
    color: str
    size: Optional[str] = None
    material: Optional[str] = None
    season: Season = Season.ALL_SEASON
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[str] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WardrobeItemCreate(WardrobeItemBase):
    image_url: str
    thumbnail_url: Optional[str] = None


class WardrobeItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[ItemCategory] = None
    subcategory: Optional[ItemSubcategory] = None
    brand: Optional[str] = None
    color: Optional[str] = None
    size: Optional[str] = None
    material: Optional[str] = None
    season: Optional[Season] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_available: Optional[bool] = None
    is_favorite: Optional[bool] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None


class WardrobeItemResponse(WardrobeItemBase):
    id: int
    user_id: int
    image_url: str
    thumbnail_url: Optional[str] = None
    is_available: bool
    is_favorite: bool
    wear_count: int
    last_worn: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
