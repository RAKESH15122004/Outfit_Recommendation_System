from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from app.schemas.outfit import OutfitResponse


class RecommendationRequest(BaseModel):
    occasion: Optional[str] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    location: Optional[str] = None
    dress_code: Optional[str] = None
    color_preferences: Optional[List[str]] = None
    brand_preferences: Optional[List[str]] = None
    comfort_level: Optional[str] = None
    budget_range: Optional[Dict[str, float]] = None
    exclude_outfit_ids: Optional[List[int]] = None  # For duplicate detection


class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    outfit_id: Optional[int] = None
    occasion: Optional[str] = None
    weather_temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    location: Optional[str] = None
    confidence_score: float
    body_type_match_score: Optional[float] = None
    color_match_score: Optional[float] = None
    style_match_score: Optional[float] = None
    trend_relevance_score: Optional[float] = None
    alternative_outfit_ids: Optional[List[int]] = None
    is_duplicate: bool
    similar_outfit_ids: Optional[List[int]] = None
    seasonal_tag: Optional[str] = None
    outfit: Optional[OutfitResponse] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RecommendationRuleCreate(BaseModel):
    rule_name: str
    rule_type: str
    rule_config: dict
    priority: int = 0
    weight: float = 1.0
    is_active: bool = True
