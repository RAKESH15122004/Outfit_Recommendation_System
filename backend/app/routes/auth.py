from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user
)
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse, RefreshTokenRequest
from app.models.user import User, UserRole
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.subscription import PlanType
from app.config import settings
from datetime import timedelta

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        body_type=user_data.body_type,
        skin_tone=user_data.skin_tone,
        preferred_colors=user_data.preferred_colors,
        brand_affinity=user_data.brand_affinity,
        comfort_level=user_data.comfort_level,
        budget_range=user_data.budget_range,
        role=UserRole.USER
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Auto-assign Basic plan so new users can try recommendations
    basic_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.plan_type == PlanType.BASIC
    ).first()
    if basic_plan:
        sub = Subscription(
            user_id=user.id,
            plan_id=basic_plan.id,
            status=SubscriptionStatus.ACTIVE,
        )
        db.add(sub)
        db.commit()
    
    return user


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create tokens (store subject as string for compatibility)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token"""
    payload = decode_token(body.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.id})
    new_refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }




@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user
