from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.middleware import SessionTimeoutMiddleware, SecurityHeadersMiddleware
from app.routes import (
    auth, users, wardrobe, outfits,
    recommendations, subscriptions, admin
)
import os

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Outfit Recommendation System API",
    description="AI-powered platform for personalized clothing suggestions",
    version="1.0.0"
)

# Middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(SessionTimeoutMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for uploads
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(wardrobe.router)
app.include_router(outfits.router)
app.include_router(recommendations.router)
app.include_router(subscriptions.router)
app.include_router(admin.router)


@app.get("/")
async def root():
    return {
        "message": "Outfit Recommendation System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
