from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.auth import get_current_admin_user
from app.schemas.recommendation import RecommendationRuleCreate
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionPlan
from app.models.recommendation import RecommendationRule, TrendAnalysis
from app.models.outfit import Outfit
from app.config import settings

router = APIRouter(prefix=f"{settings.API_V1_PREFIX}/admin", tags=["Admin"])


@router.get("/stats")
async def get_admin_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_subscriptions = db.query(Subscription).count()
    active_subscriptions = db.query(Subscription).filter(Subscription.status == "active").count()
    total_outfits = db.query(Outfit).count()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_subscriptions": total_subscriptions,
        "active_subscriptions": active_subscriptions,
        "total_outfits": total_outfits
    }


@router.get("/users", response_model=List[dict])
async def get_all_users_admin(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all users with subscription info"""
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        subscription = db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.status == "active"
        ).first()
        
        result.append({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "subscription": subscription.plan.plan_type.value if subscription else None,
            "created_at": user.created_at
        })
    
    return result


@router.get("/subscriptions", response_model=List[dict])
async def get_all_subscriptions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all subscriptions"""
    subscriptions = db.query(Subscription).offset(skip).limit(limit).all()
    
    result = []
    for sub in subscriptions:
        result.append({
            "id": sub.id,
            "user_id": sub.user_id,
            "plan": sub.plan.name,
            "status": sub.status.value,
            "start_date": sub.start_date,
            "end_date": sub.end_date
        })
    
    return result


@router.post("/recommendation-rules", status_code=status.HTTP_201_CREATED)
async def create_recommendation_rule(
    rule_data: RecommendationRuleCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create recommendation rule"""
    rule = RecommendationRule(**rule_data.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return rule


@router.get("/recommendation-rules", response_model=List[dict])
async def get_recommendation_rules(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get all recommendation rules"""
    rules = db.query(RecommendationRule).all()
    return [
        {
            "id": rule.id,
            "rule_name": rule.rule_name,
            "rule_type": rule.rule_type,
            "priority": rule.priority,
            "weight": rule.weight,
            "is_active": rule.is_active
        }
        for rule in rules
    ]


@router.put("/recommendation-rules/{rule_id}/toggle", status_code=status.HTTP_200_OK)
async def toggle_recommendation_rule(
    rule_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Toggle recommendation rule active status"""
    rule = db.query(RecommendationRule).filter(RecommendationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rule not found"
        )
    
    rule.is_active = not rule.is_active
    db.commit()
    db.refresh(rule)
    
    return {"id": rule.id, "is_active": rule.is_active}
