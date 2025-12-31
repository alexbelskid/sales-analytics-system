from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analytics, upload, email, proposals, forecast, salary
from app.routers import email_settings, inbox, tone_settings, templates, google_auth

app = FastAPI(
    title="Sales Analytics API",
    description="API для аналитической системы продаж",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get("/")
async def root():
    return {"message": "Sales Analytics API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
