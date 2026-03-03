from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.auth import get_current_active_user
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse,
    SubscriptionPlanResponse, PaymentTransactionResponse
)
from app.models.user import User
from app.models.subscription import SubscriptionPlan, Subscription, PaymentTransaction, PaymentStatus
from app.services.subscription import SubscriptionService
from app.config import settings
import stripe

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/subscriptions", tags=["Subscriptions"])


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans(db: Session = Depends(get_db)):
    """Get all available subscription plans"""
    plans = db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()
    return plans


@router.get("/plans/{plan_id}", response_model=SubscriptionPlanResponse)
async def get_subscription_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get specific subscription plan"""
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plan not found"
        )
    return plan


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current user's subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_active_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return subscription


@router.post("/checkout", status_code=status.HTTP_200_OK)
async def create_checkout_session(
    plan_id: int,
    success_url: str,
    cancel_url: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create Stripe checkout session"""
    subscription_service = SubscriptionService(db)
    
    try:
        session_data = await subscription_service.create_checkout_session(
            user=current_user,
            plan_id=plan_id,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return session_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(
    request: dict,
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    from app.config import settings
    
    # Verify webhook signature
    payload = request.get("data", {})
    event_type = request.get("type")
    
    subscription_service = SubscriptionService(db)
    result = subscription_service.handle_webhook({
        "type": event_type,
        "data": {"object": payload}
    })
    
    return result


@router.get("/transactions", response_model=List[PaymentTransactionResponse])
async def get_my_transactions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's payment transactions"""
    transactions = db.query(PaymentTransaction).filter(
        PaymentTransaction.user_id == current_user.id
    ).order_by(PaymentTransaction.created_at.desc()).all()
    
    return transactions


@router.post("/cancel", response_model=SubscriptionResponse)
async def cancel_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel current subscription"""
    subscription_service = SubscriptionService(db)
    subscription = subscription_service.get_active_subscription(current_user.id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    if subscription.stripe_subscription_id:
        # Cancel in Stripe
        stripe.Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True
        )
    
    from app.models.subscription import SubscriptionStatus
    from datetime import datetime
    subscription.status = SubscriptionStatus.CANCELLED
    subscription.cancelled_at = datetime.utcnow()
    
    db.commit()
    db.refresh(subscription)
    
    return subscription
