from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.subscription import PlanType, SubscriptionStatus, PaymentStatus


class SubscriptionPlanResponse(BaseModel):
    id: int
    plan_type: PlanType
    name: str
    description: Optional[str] = None
    daily_outfit_limit: Optional[int] = None
    ai_recommendations_enabled: bool
    wardrobe_analysis_enabled: bool
    style_forecasting_enabled: bool
    unlimited_recommendations: bool
    price_monthly: float
    price_yearly: Optional[float] = None
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_yearly: Optional[str] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class SubscriptionCreate(BaseModel):
    plan_id: int


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    stripe_subscription_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    daily_outfit_count: int
    last_reset_date: datetime
    created_at: datetime
    plan: Optional[SubscriptionPlanResponse] = None
    
    class Config:
        from_attributes = True


class PaymentTransactionResponse(BaseModel):
    id: int
    subscription_id: int
    user_id: int
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    amount: float
    currency: str
    status: PaymentStatus
    receipt_url: Optional[str] = None
    receipt_number: Optional[str] = None
    failure_reason: Optional[str] = None
    failure_code: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
