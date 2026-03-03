from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class PlanType(str, enum.Enum):
    BASIC = "basic"
    PREMIUM = "premium"


class SubscriptionStatus(str, enum.Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    PENDING = "pending"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True)
    plan_type = Column(SQLEnum(PlanType), unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Features
    daily_outfit_limit = Column(Integer, nullable=True)  # None = unlimited
    ai_recommendations_enabled = Column(Boolean, default=True)
    wardrobe_analysis_enabled = Column(Boolean, default=False)
    style_forecasting_enabled = Column(Boolean, default=False)
    unlimited_recommendations = Column(Boolean, default=False)
    
    # Pricing
    price_monthly = Column(Float, nullable=False)
    price_yearly = Column(Float, nullable=True)
    stripe_price_id_monthly = Column(String, nullable=True)
    stripe_price_id_yearly = Column(String, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    
    # Stripe details
    stripe_subscription_id = Column(String, unique=True, nullable=True)
    stripe_customer_id = Column(String, nullable=True)
    
    # Status
    status = Column(SQLEnum(SubscriptionStatus), default=SubscriptionStatus.PENDING)
    
    # Dates
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Usage tracking
    daily_outfit_count = Column(Integer, default=0)
    last_reset_date = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("SubscriptionPlan")
    transactions = relationship("PaymentTransaction", back_populates="subscription", cascade="all, delete-orphan")


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Stripe details
    stripe_payment_intent_id = Column(String, unique=True, nullable=True)
    stripe_charge_id = Column(String, nullable=True)
    
    # Transaction details
    amount = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING)
    
    # Receipt
    receipt_url = Column(String, nullable=True)
    receipt_number = Column(String, nullable=True)
    
    # Failure details
    failure_reason = Column(Text, nullable=True)
    failure_code = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="transactions")
    user = relationship("User")
