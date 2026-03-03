from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.outfit import OutfitCategory, OccasionType


class OutfitItemCreate(BaseModel):
    wardrobe_item_id: Optional[int] = None
    item_type: str
    item_name: Optional[str] = None
    item_color: Optional[str] = None
    item_image_url: Optional[str] = None
    display_order: int = 0


class OutfitItemResponse(BaseModel):
    id: int
    outfit_id: int
    wardrobe_item_id: Optional[int] = None
    item_type: str
    item_name: Optional[str] = None
    item_color: Optional[str] = None
    item_image_url: Optional[str] = None
    display_order: int
    
    class Config:
        from_attributes = True


class OutfitBase(BaseModel):
    name: Optional[str] = None
    category: OutfitCategory
    occasion: Optional[OccasionType] = None
    dress_code: Optional[str] = None
    # Stored as JSON list in the DB, but exposed as a simple list in the API
    color_preferences: Optional[list[str]] = None
    brand_preferences: Optional[list[str]] = None


class OutfitCreate(OutfitBase):
    items: List[OutfitItemCreate]
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    weather_location: Optional[str] = None


class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[OutfitCategory] = None
    occasion: Optional[OccasionType] = None
    is_saved: Optional[bool] = None
    is_favorite: Optional[bool] = None
    rating: Optional[int] = None
    preview_image_url: Optional[str] = None


class OutfitResponse(OutfitBase):
    id: int
    user_id: int
    confidence_score: float
    color_coordination_score: Optional[float] = None
    style_match_score: Optional[float] = None
    weather_appropriateness: Optional[float] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    weather_location: Optional[str] = None
    preview_image_url: Optional[str] = None
    is_ai_generated: bool
    is_saved: bool
    is_favorite: bool
    rating: Optional[int] = None
    items: List[OutfitItemResponse] = []
    created_at: datetime
    updated_at: datetime
    worn_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SavedOutfitCreate(BaseModel):
    outfit_id: int
    custom_name: Optional[str] = None
    notes: Optional[str] = None
    reminder_date: Optional[datetime] = None


class SavedOutfitResponse(BaseModel):
    id: int
    user_id: int
    outfit_id: int
    custom_name: Optional[str] = None
    notes: Optional[str] = None
    reminder_date: Optional[datetime] = None
    reminder_sent: bool
    created_at: datetime
    outfit: Optional[OutfitResponse] = None
    
    class Config:
        from_attributes = True
