"""
AI Router - Google Gemini Integration
Handles AI-powered email response generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

from app.services.gemini_service import gemini_service

logger = logging.getLogger(__name__)

router = APIRouter()


class GenerateRequest(BaseModel):
    """Request model for AI response generation"""
    email_from: str
    email_subject: str
    email_body: str
    tone: str = "professional"
    context: Optional[str] = None  # Optional knowledge base context


class GenerateResponse(BaseModel):
    """Response model for AI generation"""
    success: bool
    response: str
    confidence: float
    model: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-response", response_model=GenerateResponse)
async def generate_ai_response(request: GenerateRequest):
    """
    Generate AI-powered email response using Google Gemini
    
    Args:
        request: Generation request with email details and context
        
    Returns:
        Generated response with confidence score
    """
    
    try:
        # Check if Gemini is available
        if not gemini_service.is_available():
            raise HTTPException(
                status_code=503,
                detail="Gemini API не настроен. Добавьте GOOGLE_GEMINI_API_KEY в настройках."
            )
        
        # Generate response
        result = await gemini_service.generate_response(
            email_from=request.email_from,
            email_subject=request.email_subject,
            email_body=request.email_body,
            tone=request.tone,
            knowledge_base=request.context,
            training_examples=None  # Will be added in Phase 2
        )
        
        return GenerateResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_ai_status():
    """
    Check AI service status
    
    Returns:
        Status information about Gemini API
    """
    
    return {
        "available": gemini_service.is_available(),
        "model": gemini_service.model_name if gemini_service.is_available() else None,
        "api_key_configured": gemini_service.api_key is not None
    }
