from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.auth import get_current_active_user
from app.schemas.wardrobe import WardrobeItemCreate, WardrobeItemUpdate, WardrobeItemResponse
from app.models.wardrobe import WardrobeItem, ItemCategory
from app.models.user import User
from app.services.file_upload import file_upload_service
from app.config import settings

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/wardrobe", tags=["Wardrobe"])


@router.post("/items", response_model=WardrobeItemResponse, status_code=status.HTTP_201_CREATED)
async def create_wardrobe_item(
    item_data: WardrobeItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add a new wardrobe item"""
    item = WardrobeItem(
        user_id=current_user.id,
        **item_data.model_dump()
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/items/upload", response_model=WardrobeItemResponse, status_code=status.HTTP_201_CREATED)
async def upload_wardrobe_item(
    file: UploadFile = File(...),
    name: str | None = None,
    category: ItemCategory = ItemCategory.TOP,
    color: str | None = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload wardrobe item with image"""
    # Upload image
    upload_result = await file_upload_service.upload_image(file, current_user.id, "wardrobe")
    
    # Create item, ensuring category is a valid ItemCategory enum
    item = WardrobeItem(
        user_id=current_user.id,
        name=name or file.filename,
        category=category,
        color=color or "unknown",
        image_url=upload_result["image_url"],
        thumbnail_url=upload_result["thumbnail_url"],
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/items", response_model=List[WardrobeItemResponse])
async def get_wardrobe_items(
    category: Optional[ItemCategory] = None,
    is_available: Optional[bool] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's wardrobe items"""
    query = db.query(WardrobeItem).filter(WardrobeItem.user_id == current_user.id)
    
    if category:
        query = query.filter(WardrobeItem.category == category)
    if is_available is not None:
        query = query.filter(WardrobeItem.is_available == is_available)
    
    items = query.all()
    return items


@router.get("/items/{item_id}", response_model=WardrobeItemResponse)
async def get_wardrobe_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific wardrobe item"""
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wardrobe item not found"
        )
    
    return item


@router.put("/items/{item_id}", response_model=WardrobeItemResponse)
async def update_wardrobe_item(
    item_id: int,
    item_update: WardrobeItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update wardrobe item"""
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wardrobe item not found"
        )
    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wardrobe_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete wardrobe item"""
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wardrobe item not found"
        )
    
    # Delete associated file
    if item.image_url:
        file_upload_service.delete_file(item.image_url)
    
    db.delete(item)
    db.commit()
    return None


@router.get("/items/{item_id}/mark-worn", response_model=WardrobeItemResponse)
async def mark_item_worn(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark wardrobe item as worn"""
    item = db.query(WardrobeItem).filter(
        WardrobeItem.id == item_id,
        WardrobeItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wardrobe item not found"
        )
    
    item.wear_count += 1
    item.last_worn = datetime.utcnow()
    
    db.commit()
    db.refresh(item)
    return item
