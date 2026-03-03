from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_active_user
from app.schemas.recommendation import RecommendationRequest, RecommendationResponse
from app.models.user import User
from app.models.recommendation import Recommendation
from app.models.outfit import Outfit, SavedOutfit
from app.services.recommendation_engine import RecommendationEngine
from app.services.subscription import SubscriptionService
from app.services.weather import weather_service
from app.config import settings

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["Recommendations"])


@router.post("/generate", response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
async def generate_recommendation(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate AI-powered outfit recommendation"""
    # Check subscription
    subscription_service = SubscriptionService(db)
    if not subscription_service.can_generate_outfit(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription limit reached. Please upgrade to premium for unlimited recommendations."
        )
    
    # Get weather if location provided
    weather_data = None
    if request.location:
        weather_data = await weather_service.get_weather(request.location)
        if weather_data:
            request.weather_temperature = request.weather_temperature or weather_data.get("temperature")
            request.weather_condition = request.weather_condition or weather_data.get("condition")
    
    # Generate recommendation
    engine = RecommendationEngine(db)
    try:
        recommendation = await engine.generate_recommendation(
            user=current_user,
            occasion=request.occasion,
            weather_temperature=request.weather_temperature,
            weather_condition=request.weather_condition,
            location=request.location,
            dress_code=request.dress_code,
            color_preferences=request.color_preferences,
            brand_preferences=request.brand_preferences,
            exclude_outfit_ids=request.exclude_outfit_ids
        )
        
        # Increment outfit count
        subscription_service.increment_outfit_count(current_user.id)
        
        return recommendation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[RecommendationResponse])
async def get_recommendations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's recommendation history (excluding rejected/expired)"""
    recommendations = (
        db.query(Recommendation)
        .filter(
            Recommendation.user_id == current_user.id,
            Recommendation.status != "rejected",
        )
        .order_by(Recommendation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    return recommendation


@router.post("/{recommendation_id}/accept", response_model=RecommendationResponse)
async def accept_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Accept a recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    from app.models.recommendation import RecommendationStatus
    recommendation.status = RecommendationStatus.ACCEPTED

    # If this recommendation points to an outfit, ensure it's saved to favorites
    if recommendation.outfit_id:
        outfit = db.query(Outfit).filter(Outfit.id == recommendation.outfit_id).first()
        if outfit:
            outfit.is_saved = True
            outfit.is_favorite = True

            # Create SavedOutfit entry if it doesn't already exist
            existing = (
                db.query(SavedOutfit)
                .filter(
                    SavedOutfit.user_id == current_user.id,
                    SavedOutfit.outfit_id == outfit.id,
                )
                .first()
            )
            if not existing:
                saved = SavedOutfit(user_id=current_user.id, outfit_id=outfit.id)
                db.add(saved)

    db.commit()
    db.refresh(recommendation)

    return recommendation


@router.post("/{recommendation_id}/reject", response_model=RecommendationResponse)
async def reject_recommendation(
    recommendation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reject a recommendation"""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == current_user.id
    ).first()
    
    if not recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    from app.models.recommendation import RecommendationStatus
    recommendation.status = RecommendationStatus.REJECTED
    
    db.commit()
    db.refresh(recommendation)
    
    return recommendation
