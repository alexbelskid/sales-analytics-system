from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from app.routers import analytics, upload, email, proposals, forecast, salary
from app.routers import email_settings, inbox, tone_settings, templates, google_auth, ai, knowledge, training, data_upload

app = FastAPI(
    title="Alterini AI API",
    description="API для аналитической системы продаж с AI-ассистентом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # Local development
        "http://127.0.0.1:3000",      # Local development alt
        "https://sales-analytics-system-psi.vercel.app",  # Vercel production
        "*"  # Allow all for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(email.router, prefix="/api/email", tags=["Legacy Email"])
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
