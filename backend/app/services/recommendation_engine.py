from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.wardrobe import WardrobeItem, ItemCategory
from app.models.outfit import Outfit, OutfitItem, OutfitCategory
from app.models.recommendation import Recommendation, RecommendationStatus
from app.services.weather import weather_service
import random
from datetime import datetime


class RecommendationEngine:
    def __init__(self, db: Session):
        self.db = db
    
    async def generate_recommendation(
        self,
        user: User,
        occasion: Optional[str] = None,
        weather_temperature: Optional[float] = None,
        weather_condition: Optional[str] = None,
        location: Optional[str] = None,
        dress_code: Optional[str] = None,
        color_preferences: Optional[List[str]] = None,
        brand_preferences: Optional[List[str]] = None,
        exclude_outfit_ids: Optional[List[int]] = None
    ) -> Recommendation:
        """Generate AI-powered outfit recommendation"""
        
        # Get user's wardrobe items
        wardrobe_items = self.db.query(WardrobeItem).filter(
            WardrobeItem.user_id == user.id,
            WardrobeItem.is_available == True
        ).all()
        
        if not wardrobe_items:
            raise ValueError("No wardrobe items available")
        
        # Determine outfit category based on occasion
        outfit_category = self._determine_category(occasion, dress_code)
        
        # Filter items by category and preferences
        filtered_items = self._filter_items(
            wardrobe_items,
            outfit_category,
            color_preferences or user.preferred_colors or [],
            brand_preferences or user.brand_affinity or [],
            weather_temperature
        )
        
        # Generate outfit combination
        outfit_items = self._create_outfit_combination(
            filtered_items,
            outfit_category,
            weather_temperature,
            weather_condition
        )
        
        if not outfit_items:
            raise ValueError("Could not create outfit combination")
        
        # Calculate scores
        confidence_score = self._calculate_confidence_score(
            outfit_items,
            user,
            color_preferences or user.preferred_colors or [],
            weather_temperature
        )
        
        body_type_score = self._calculate_body_type_match(outfit_items, user.body_type)
        color_score = self._calculate_color_match(outfit_items, user.skin_tone, color_preferences)
        style_score = self._calculate_style_match(outfit_items, outfit_category)
        
        # Check for duplicates
        is_duplicate, similar_outfit_ids = self._check_duplicates(
            user.id,
            outfit_items,
            exclude_outfit_ids or []
        )
        
        # Create outfit
        outfit = Outfit(
            user_id=user.id,
            category=outfit_category,
            occasion=occasion,
            dress_code=dress_code,
            weather_temperature=weather_temperature,
            weather_condition=weather_condition,
            weather_location=location,
            confidence_score=confidence_score,
            color_coordination_score=color_score,
            style_match_score=style_score,
            color_preferences=color_preferences or user.preferred_colors,
            brand_preferences=brand_preferences or user.brand_affinity,
            is_ai_generated=True
        )
        self.db.add(outfit)
        self.db.flush()
        
        # Create outfit items
        for idx, item in enumerate(outfit_items):
            outfit_item = OutfitItem(
                outfit_id=outfit.id,
                wardrobe_item_id=item.id,
                item_type=item.category.value,
                item_name=item.name,
                item_color=item.color,
                item_image_url=item.image_url,
                display_order=idx
            )
            self.db.add(outfit_item)
        
        # Create recommendation record
        recommendation = Recommendation(
            user_id=user.id,
            outfit_id=outfit.id,
            occasion=occasion,
            weather_temperature=weather_temperature,
            weather_condition=weather_condition,
            location=location,
            body_type_used=user.body_type,
            skin_tone_used=user.skin_tone,
            color_preferences_used=color_preferences or user.preferred_colors,
            confidence_score=confidence_score,
            body_type_match_score=body_type_score,
            color_match_score=color_score,
            style_match_score=style_score,
            status=RecommendationStatus.GENERATED,
            is_duplicate=is_duplicate,
            similar_outfit_ids=similar_outfit_ids,
            seasonal_tag=self._get_seasonal_tag(weather_temperature)
        )
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        
        return recommendation
    
    def _determine_category(self, occasion: Optional[str], dress_code: Optional[str]) -> OutfitCategory:
        """Determine outfit category from occasion and dress code"""
        if dress_code in ["formal", "business", "corporate"]:
            return OutfitCategory.FORMAL_WEAR
        
        if occasion in ["wedding", "party", "festival", "special_event"]:
            return OutfitCategory.OCCASION_WEAR
        
        return OutfitCategory.CASUAL_WEAR
    
    def _filter_items(
        self,
        items: List[WardrobeItem],
        category: OutfitCategory,
        color_preferences: List[str],
        brand_preferences: List[str],
        temperature: Optional[float]
    ) -> List[WardrobeItem]:
        """Filter wardrobe items based on preferences"""
        filtered = []
        
        for item in items:
            # Filter by season/weather
            if temperature is not None:
                if temperature < 10 and item.season.value == "summer":
                    continue
                if temperature > 25 and item.season.value == "winter":
                    continue
            
            # Filter by color preferences if provided
            if color_preferences and item.color.lower() not in [c.lower() for c in color_preferences]:
                # Still include but with lower priority
                pass
            
            # Filter by brand preferences if provided
            if brand_preferences and item.brand and item.brand.lower() not in [b.lower() for b in brand_preferences]:
                # Still include but with lower priority
                pass
            
            filtered.append(item)
        
        return filtered if filtered else items
    
    def _create_outfit_combination(
        self,
        items: List[WardrobeItem],
        category: OutfitCategory,
        temperature: Optional[float],
        condition: Optional[str]
    ) -> List[WardrobeItem]:
        """Create a complete outfit combination"""
        outfit_items = []
        
        # Get items by category
        tops = [i for i in items if i.category == ItemCategory.TOP]
        bottoms = [i for i in items if i.category == ItemCategory.BOTTOM]
        footwear = [i for i in items if i.category == ItemCategory.FOOTWEAR]
        accessories = [i for i in items if i.category == ItemCategory.ACCESSORY]
        outerwear = [i for i in items if i.category == ItemCategory.OUTERWEAR]
        dresses = [i for i in items if i.category == ItemCategory.DRESS]
        
        # If dress, return dress + footwear + accessories
        if dresses and category == OutfitCategory.OCCASION_WEAR:
            outfit_items.append(random.choice(dresses))
            if footwear:
                outfit_items.append(random.choice(footwear))
            if accessories:
                outfit_items.append(random.choice(accessories[:2]))
            return outfit_items
        
        # Otherwise, build combination
        if tops:
            outfit_items.append(random.choice(tops))
        if bottoms:
            outfit_items.append(random.choice(bottoms))
        if footwear:
            outfit_items.append(random.choice(footwear))
        
        # Add outerwear based on temperature
        if temperature and temperature < 15 and outerwear:
            outfit_items.append(random.choice(outerwear))
        
        # Add accessories
        if accessories:
            outfit_items.append(random.choice(accessories))
        
        return outfit_items
    
    def _calculate_confidence_score(
        self,
        items: List[WardrobeItem],
        user: User,
        color_preferences: List[str],
        temperature: Optional[float]
    ) -> float:
        """Calculate overall confidence score"""
        score = 0.5  # Base score
        
        # Color coordination
        if len(items) > 1:
            colors = [item.color.lower() for item in items]
            unique_colors = len(set(colors))
            if unique_colors <= 3:  # Good coordination
                score += 0.2
        
        # User preferences match
        if color_preferences:
            matching_colors = sum(1 for item in items if item.color.lower() in [c.lower() for c in color_preferences])
            score += (matching_colors / len(items)) * 0.2
        
        # Weather appropriateness
        if temperature:
            if 15 <= temperature <= 25:
                score += 0.1
        
        return min(score, 1.0)
    
    def _calculate_body_type_match(self, items: List[WardrobeItem], body_type: Optional[str]) -> Optional[float]:
        """Calculate body type match score"""
        if not body_type:
            return None
        
        # Simplified body type matching logic
        # In production, this would use ML models
        return 0.75  # Placeholder
    
    def _calculate_color_match(
        self,
        items: List[WardrobeItem],
        skin_tone: Optional[str],
        color_preferences: Optional[List[str]]
    ) -> Optional[float]:
        """Calculate color match score based on skin tone"""
        if not skin_tone:
            return None
        
        # Simplified color matching logic
        # Warm tones: earth tones, warm colors
        # Cool tones: blues, purples, cool colors
        # Neutral: can wear both
        
        score = 0.7  # Base score
        
        if color_preferences:
            matching = sum(1 for item in items if item.color.lower() in [c.lower() for c in color_preferences])
            score += (matching / len(items)) * 0.2
        
        return min(score, 1.0)
    
    def _calculate_style_match(self, items: List[WardrobeItem], category: OutfitCategory) -> float:
        """Calculate style match score"""
        # Simplified style matching
        return 0.8  # Placeholder
    
    def _check_duplicates(
        self,
        user_id: int,
        items: List[WardrobeItem],
        exclude_ids: List[int]
    ) -> Tuple[bool, List[int]]:
        """Check for duplicate outfits"""
        item_ids = [item.id for item in items]
        
        # Get existing outfits for user
        existing_outfits = self.db.query(Outfit).filter(
            Outfit.user_id == user_id,
            Outfit.id.notin_(exclude_ids)
        ).all()
        
        similar_outfit_ids = []
        for outfit in existing_outfits:
            outfit_item_ids = [oi.wardrobe_item_id for oi in outfit.items if oi.wardrobe_item_id]
            if set(item_ids) == set(outfit_item_ids):
                similar_outfit_ids.append(outfit.id)
        
        return len(similar_outfit_ids) > 0, similar_outfit_ids
    
    def _get_seasonal_tag(self, temperature: Optional[float]) -> Optional[str]:
        """Get seasonal tag based on temperature"""
        if not temperature:
            return None
        
        if temperature < 5:
            return "winter"
        elif temperature < 15:
            return "fall"
        elif temperature < 25:
            return "spring"
        else:
            return "summer"

