from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import os
import logging
import uuid
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import analytics, upload, proposals, forecast, salary
from app.routers import email_settings, inbox, tone_settings, templates, google_auth, ai, knowledge, training, data_upload, advanced_analytics, plan_fact

# Configure logging
logger = logging.getLogger(__name__)

# SECURITY: Rate limiting configuration
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Alterini AI API",
    description="API для аналитической системы продаж с AI-ассистентом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state and exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS Configuration - SECURITY: Only allow trusted origins
# Get additional origins from environment variable if needed
_extra_origins = os.getenv("CORS_ORIGINS", "").split(",")
_extra_origins = [o.strip() for o in _extra_origins if o.strip()]

ALLOWED_ORIGINS = [
    "http://localhost:3000",      # Local development
    "http://127.0.0.1:3000",      # Local development alt
    "https://sales-analytics-system-psi.vercel.app",  # Vercel production
] + _extra_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
)


# SECURITY: Global exception handler - prevents internal error details from leaking
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Catch all unhandled exceptions and return a sanitized error response.
    Full error details are logged server-side only.
    """
    error_id = str(uuid.uuid4())[:8]  # Short unique ID for tracking
    
    # Log full error details server-side
    logger.error(
        f"Error ID: {error_id} | Path: {request.url.path} | "
        f"Method: {request.method} | Error: {type(exc).__name__}: {str(exc)}"
    )
    
    # Return sanitized response to client
    is_development = os.getenv("ENVIRONMENT", "development") == "development"
    
    if is_development:
        # In dev, show more details for debugging
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_id": error_id,
                "detail": str(exc),  # Only in development!
                "type": type(exc).__name__
            }
        )
    else:
        # In production, hide all details
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "error_id": error_id,
                "message": "An unexpected error occurred. Contact support with this error ID."
            }
        )


# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(salary.router, prefix="/api/salary", tags=["Salary"])

# New Email System Routers
app.include_router(email_settings.router, prefix="/api/emails/settings", tags=["Email Settings"])
app.include_router(inbox.router, prefix="/api/emails", tags=["Inbox"])
app.include_router(tone_settings.router, prefix="/api/tone-settings", tags=["Tone Settings"])
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(google_auth.router, prefix="/api/google", tags=["Google Auth"])

# AI System Router
app.include_router(ai.router, prefix="/api/ai", tags=["AI"])

# Knowledge Base & Training
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["Knowledge Base"])
app.include_router(training.router, prefix="/api/training", tags=["Training"])

# Data Integration (CSV upload + analytics summary)
app.include_router(data_upload.router)

# Excel Import Router
from app.routers import import_router
app.include_router(import_router.router)

# Extended Analytics Router
from app.routers import extended_analytics
app.include_router(extended_analytics.router)

# Files Management Router
from app.routers import files_router
app.include_router(files_router.router)

# Agent Analytics Router
from app.routers import agent_analytics
app.include_router(agent_analytics.router, prefix="/api")

# Advanced Analytics Router (LFL, Filters)
app.include_router(advanced_analytics.router, prefix="/api/analytics", tags=["Advanced Analytics"])

# Plan-Fact Analysis Router
app.include_router(plan_fact.router, prefix="/api/analytics", tags=["Plan-Fact"])


@app.get("/", tags=["Health"])
async def root():
    """API информация и статус"""
    return {
        "name": "Alterini AI API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/api/health", tags=["Health"])
async def api_health():
    """Детальная проверка здоровья API"""
    return {
        "status": "healthy",
        "service": "alterini-ai-backend",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "ok",
            "database": "check /api/data/analytics/summary"
        }
    }
