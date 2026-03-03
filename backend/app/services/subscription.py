import stripe
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.config import settings
from app.models.subscription import Subscription, SubscriptionPlan, SubscriptionStatus, PlanType
from app.models.user import User

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get user's active subscription"""
        return self.db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == SubscriptionStatus.ACTIVE
        ).first()
    
    def can_generate_outfit(self, user_id: int) -> bool:
        """Check if user can generate outfit based on subscription"""
        subscription = self.get_active_subscription(user_id)

        # If user has no active subscription, try to automatically attach the Basic plan
        # so local/dev users can immediately generate outfits after registration.
        if not subscription:
            basic_plan = self.db.query(SubscriptionPlan).filter(
                SubscriptionPlan.plan_type == PlanType.BASIC,
                SubscriptionPlan.is_active == True,
            ).first()

            if basic_plan:
                subscription = Subscription(
                    user_id=user_id,
                    plan_id=basic_plan.id,
                    status=SubscriptionStatus.ACTIVE,
                    start_date=datetime.utcnow(),
                    last_reset_date=datetime.utcnow(),
                    daily_outfit_count=0,
                )
                self.db.add(subscription)
                self.db.commit()
                return True

            # If no plans are configured at all, don't block outfit generation in dev
            return True
        
        plan = subscription.plan

        # Premium plan has unlimited
        if plan.unlimited_recommendations:
            return True

        # Check daily limit
        if plan.daily_outfit_limit is not None:
            # Reset daily count if needed
            if subscription.last_reset_date.date() < datetime.utcnow().date():
                subscription.daily_outfit_count = 0
                subscription.last_reset_date = datetime.utcnow()
                self.db.commit()

            # For the Basic plan in this project, we want up to 20
            # recommendations per day, even if the stored limit is lower.
            effective_limit = plan.daily_outfit_limit
            if plan.plan_type == PlanType.BASIC and effective_limit < 20:
                effective_limit = 20

            if subscription.daily_outfit_count >= effective_limit:
                return False
        
        return True
    
    def increment_outfit_count(self, user_id: int):
        """Increment daily outfit count"""
        subscription = self.get_active_subscription(user_id)
        if subscription:
            subscription.daily_outfit_count += 1
            self.db.commit()
    
    async def create_checkout_session(
        self,
        user: User,
        plan_id: int,
        success_url: str,
        cancel_url: str
    ) -> dict:
        """Create Stripe checkout session"""
        plan = self.db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
        if not plan:
            raise ValueError("Plan not found")
        if not plan.stripe_price_id_monthly or not settings.STRIPE_SECRET_KEY:
            raise ValueError(
                "Stripe is not configured. Add STRIPE_SECRET_KEY to .env and "
                "set stripe_price_id_monthly for plans via Stripe dashboard."
            )

        # Create or get Stripe customer
        customer_id = await self._get_or_create_customer(user)
        
        # Create checkout session
        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[{
                "price": plan.stripe_price_id_monthly,
                "quantity": 1,
            }],
            mode="subscription",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "user_id": user.id,
                "plan_id": plan_id
            }
        )
        
        return {
            "session_id": session.id,
            "url": session.url
        }
    
    async def _get_or_create_customer(self, user: User) -> str:
        """Get or create Stripe customer"""
        # Check if user has existing subscription with customer_id
        existing_sub = self.db.query(Subscription).filter(
            Subscription.user_id == user.id,
            Subscription.stripe_customer_id.isnot(None)
        ).first()
        
        if existing_sub and existing_sub.stripe_customer_id:
            return existing_sub.stripe_customer_id
        
        # Create new customer
        customer = stripe.Customer.create(
            email=user.email,
            name=user.full_name,
            metadata={"user_id": user.id}
        )
        
        return customer.id
    
    def handle_webhook(self, event: dict) -> dict:
        """Handle Stripe webhook events"""
        event_type = event.get("type")
        data = event.get("data", {}).get("object", {})
        
        if event_type == "checkout.session.completed":
            return self._handle_checkout_completed(data)
        elif event_type == "customer.subscription.updated":
            return self._handle_subscription_updated(data)
        elif event_type == "customer.subscription.deleted":
            return self._handle_subscription_deleted(data)
        elif event_type == "invoice.payment_failed":
            return self._handle_payment_failed(data)
        
        return {"status": "ignored"}
    
    def _handle_checkout_completed(self, session: dict) -> dict:
        """Handle successful checkout"""
        user_id = session.get("metadata", {}).get("user_id")
        plan_id = session.get("metadata", {}).get("plan_id")
        subscription_id = session.get("subscription")
        
        if not user_id or not plan_id:
            return {"status": "error", "message": "Missing metadata"}
        
        # Create subscription record
        subscription = Subscription(
            user_id=int(user_id),
            plan_id=int(plan_id),
            stripe_subscription_id=subscription_id,
            stripe_customer_id=session.get("customer"),
            status=SubscriptionStatus.ACTIVE,
            start_date=datetime.utcnow()
        )
        self.db.add(subscription)
        self.db.commit()
        
        return {"status": "success"}
    
    def _handle_subscription_updated(self, subscription: dict) -> dict:
        """Handle subscription update"""
        stripe_sub_id = subscription.get("id")
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()
        
        if sub:
            status_map = {
                "active": SubscriptionStatus.ACTIVE,
                "canceled": SubscriptionStatus.CANCELLED,
                "past_due": SubscriptionStatus.EXPIRED
            }
            sub.status = status_map.get(subscription.get("status"), SubscriptionStatus.ACTIVE)
            self.db.commit()
        
        return {"status": "success"}
    
    def _handle_subscription_deleted(self, subscription: dict) -> dict:
        """Handle subscription cancellation"""
        stripe_sub_id = subscription.get("id")
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == stripe_sub_id
        ).first()
        
        if sub:
            sub.status = SubscriptionStatus.CANCELLED
            sub.cancelled_at = datetime.utcnow()
            self.db.commit()
        
        return {"status": "success"}
    
    def _handle_payment_failed(self, invoice: dict) -> dict:
        """Handle failed payment"""
        # Create failed transaction record
        subscription_id = invoice.get("subscription")
        sub = self.db.query(Subscription).filter(
            Subscription.stripe_subscription_id == subscription_id
        ).first()
        
        if sub:
            from app.models.subscription import PaymentTransaction, PaymentStatus
            transaction = PaymentTransaction(
                subscription_id=sub.id,
                user_id=sub.user_id,
                stripe_payment_intent_id=invoice.get("payment_intent"),
                amount=invoice.get("amount_due", 0) / 100,  # Convert from cents
                status=PaymentStatus.FAILED,
                failure_reason=invoice.get("last_payment_error", {}).get("message"),
                failure_code=invoice.get("last_payment_error", {}).get("code")
            )
            self.db.add(transaction)
            self.db.commit()
        
        return {"status": "success"}
