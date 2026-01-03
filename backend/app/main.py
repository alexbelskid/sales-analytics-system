from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analytics, upload, email, proposals, forecast, salary
from app.routers import email_settings, inbox, tone_settings, templates, google_auth, ai, knowledge, training, data_upload

app = FastAPI(
    title="Sales Analytics API",
    description="API для аналитической системы продаж",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://sales-analytics-system-psi.vercel.app",
        "*"
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


@app.get("/")
async def root():
    return {"message": "Sales Analytics API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/health")
async def api_health():
    return {"status": "ok", "service": "sales-ai-backend", "version": "1.0.0"}
