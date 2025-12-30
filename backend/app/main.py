from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analytics, upload, email, proposals, forecast, salary

app = FastAPI(
    title="Sales Analytics API",
    description="API для аналитики продаж, автоответов, КП и прогнозирования",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(email.router, prefix="/api/email", tags=["Email"])
app.include_router(proposals.router, prefix="/api/proposals", tags=["Proposals"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Forecast"])
app.include_router(salary.router, prefix="/api/salary", tags=["Salary"])


@app.get("/")
async def root():
    return {"message": "Sales Analytics API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}
