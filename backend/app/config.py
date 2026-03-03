from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    # Database - default SQLite for local dev
    DATABASE_URL: str = "sqlite:///./outfit.db"
    
    # JWT
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Stripe - optional for local dev (checkout will fail without valid keys)
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    # Weather API - optional for local dev
    WEATHER_API_KEY: Optional[str] = None
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5/weather"
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Application
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]
    
    # Admin
    DEFAULT_ADMIN_EMAIL: str = "admin@outfit.com"
    DEFAULT_ADMIN_PASSWORD: str = "admin123"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
