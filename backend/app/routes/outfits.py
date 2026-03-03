from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_active_user
from app.schemas.outfit import (
    OutfitCreate, OutfitUpdate, OutfitResponse,
    SavedOutfitCreate, SavedOutfitResponse
)
from app.models.outfit import Outfit, SavedOutfit
from app.models.user import User
from app.config import settings

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/outfits", tags=["Outfits"])


@router.get("/", response_model=List[OutfitResponse])
async def get_outfits(
    category: Optional[str] = None,
    is_saved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's outfits"""
    query = db.query(Outfit).filter(Outfit.user_id == current_user.id)
    
    if category:
        query = query.filter(Outfit.category == category)
    if is_saved is not None:
        query = query.filter(Outfit.is_saved == is_saved)
    
    outfits = query.order_by(Outfit.created_at.desc()).offset(skip).limit(limit).all()
    return outfits


@router.get("/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific outfit"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    return outfit


@router.put("/{outfit_id}", response_model=OutfitResponse)
async def update_outfit(
    outfit_id: int,
    outfit_update: OutfitUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update outfit"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    update_data = outfit_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(outfit, field, value)
    
    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete outfit"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    db.delete(outfit)
    db.commit()
    return None


@router.post("/{outfit_id}/save", response_model=SavedOutfitResponse, status_code=status.HTTP_201_CREATED)
async def save_outfit(
    outfit_id: int,
    saved_outfit_data: SavedOutfitCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Save outfit to favorites"""
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    # Check if already saved
    existing = db.query(SavedOutfit).filter(
        SavedOutfit.user_id == current_user.id,
        SavedOutfit.outfit_id == outfit_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Outfit already saved"
        )
    
    saved_outfit = SavedOutfit(
        user_id=current_user.id,
        outfit_id=outfit_id,
        custom_name=saved_outfit_data.custom_name,
        notes=saved_outfit_data.notes,
        reminder_date=saved_outfit_data.reminder_date
    )
    
    outfit.is_saved = True
    outfit.is_favorite = True
    
    db.add(saved_outfit)
    db.commit()
    db.refresh(saved_outfit)
    
    return saved_outfit


@router.get("/saved/list", response_model=List[SavedOutfitResponse])
async def get_saved_outfits(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all saved outfits"""
    saved_outfits = db.query(SavedOutfit).filter(
        SavedOutfit.user_id == current_user.id
    ).order_by(SavedOutfit.created_at.desc()).all()
    
    return saved_outfits


@router.delete("/saved/{saved_outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unsave_outfit(
    saved_outfit_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Remove outfit from saved"""
    saved_outfit = db.query(SavedOutfit).filter(
        SavedOutfit.id == saved_outfit_id,
        SavedOutfit.user_id == current_user.id
    ).first()
    
    if not saved_outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Saved outfit not found"
        )
    
    # Update outfit
    outfit = db.query(Outfit).filter(Outfit.id == saved_outfit.outfit_id).first()
    if outfit:
        outfit.is_saved = False
        outfit.is_favorite = False
    
    db.delete(saved_outfit)
    db.commit()
    return None


@router.post("/{outfit_id}/rate", response_model=OutfitResponse)
async def rate_outfit(
    outfit_id: int,
    rating: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Rate an outfit (1-5 stars)"""
    if rating < 1 or rating > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1 and 5"
        )
    
    outfit = db.query(Outfit).filter(
        Outfit.id == outfit_id,
        Outfit.user_id == current_user.id
    ).first()
    
    if not outfit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outfit not found"
        )
    
    outfit.rating = rating
    db.commit()
    db.refresh(outfit)
    
    return outfit
