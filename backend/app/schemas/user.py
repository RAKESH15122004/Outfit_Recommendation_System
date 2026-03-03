from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    preferred_colors: Optional[list] = None
    brand_affinity: Optional[list] = None
    comfort_level: Optional[str] = None
    budget_range: Optional[dict] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    body_type: Optional[str] = None
    skin_tone: Optional[str] = None
    preferred_colors: Optional[list] = None
    brand_affinity: Optional[list] = None
    comfort_level: Optional[str] = None
    budget_range: Optional[dict] = None
    profile_image_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    profile_image_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
