"""
Initialize database with default data
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.user import User, UserRole
from app.models.subscription import SubscriptionPlan, PlanType
from app.auth import get_password_hash
from app.config import settings

# Create all tables
Base.metadata.create_all(bind=engine)


def init_default_admin():
    """Create default admin user"""
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                email=settings.DEFAULT_ADMIN_EMAIL,
                hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"Created admin user: {settings.DEFAULT_ADMIN_EMAIL}")
        else:
            print(f"Admin user already exists: {settings.DEFAULT_ADMIN_EMAIL}")
    finally:
        db.close()


def init_subscription_plans():
    """Create default subscription plans"""
    db = SessionLocal()
    try:
        # Basic Plan
        basic_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_type == PlanType.BASIC
        ).first()
        
        if not basic_plan:
            basic_plan = SubscriptionPlan(
                plan_type=PlanType.BASIC,
                name="Basic Plan",
                description="Up to 20 AI outfit suggestions per day",
                daily_outfit_limit=20,
                ai_recommendations_enabled=True,
                wardrobe_analysis_enabled=False,
                style_forecasting_enabled=False,
                unlimited_recommendations=False,
                price_monthly=9.99,
                price_yearly=99.99,
                is_active=True
            )
            db.add(basic_plan)
            print("Created Basic Plan")
        else:
            print("Basic Plan already exists")
        
        # Premium Plan
        premium_plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.plan_type == PlanType.PREMIUM
        ).first()
        
        if not premium_plan:
            premium_plan = SubscriptionPlan(
                plan_type=PlanType.PREMIUM,
                name="Premium Plan",
                description="Unlimited AI recommendations, wardrobe analysis, and style forecasting",
                daily_outfit_limit=None,  # Unlimited
                ai_recommendations_enabled=True,
                wardrobe_analysis_enabled=True,
                style_forecasting_enabled=True,
                unlimited_recommendations=True,
                price_monthly=19.99,
                price_yearly=199.99,
                is_active=True
            )
            db.add(premium_plan)
            print("Created Premium Plan")
        else:
            print("Premium Plan already exists")
        
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_default_admin()
    init_subscription_plans()
    print("Database initialization complete!")
