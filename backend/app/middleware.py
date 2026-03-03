from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from app.config import settings


class SessionTimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to handle session timeout"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip for public endpoints
        if request.url.path.startswith(f"{settings.API_V1_PREFIX}/auth") or \
           request.url.path.startswith("/docs") or \
           request.url.path.startswith("/openapi.json") or \
           request.url.path == "/" or \
           request.url.path == "/health":
            return await call_next(request)
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
