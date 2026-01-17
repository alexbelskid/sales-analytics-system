"""
AI Router - Groq Integration
Handles AI-powered email response generation
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import logging

from app.services.groq_service import GroqService
from app.services.company_knowledge_service import company_knowledge_service
from slowapi import Limiter
from slowapi.util import get_remote_address

logger = logging.getLogger(__name__)

router = APIRouter()
groq_service = GroqService()

# Rate limiter for AI endpoints (expensive operations)
limiter = Limiter(key_func=get_remote_address)


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
    confidence: float = 0.0
    model: Optional[str] = None
    error: Optional[str] = None


@router.post("/generate-response", response_model=GenerateResponse)
@limiter.limit("20/minute")
async def generate_ai_response(request: Request, gen_request: GenerateRequest):
    """
    Generate AI-powered email response using Groq
    
    Args:
        request: Generation request with email details and context
        
    Returns:
        Generated response with confidence score
    """
    
    try:
        status = groq_service.check_status()
        if not status.get("available"):
            raise HTTPException(
                status_code=503,
                detail="Groq API не настроен. Добавьте GROQ_API_KEY в настройках."
            )
        
        # Pass all details to service which handles context fetching
        response_text = await groq_service.generate_response(
            email_from=gen_request.email_from,
            email_subject=gen_request.email_subject,
            email_body=gen_request.email_body,
            tone=gen_request.tone,
            knowledge_base=gen_request.context,
            training_examples=None,
            include_analytics=True
        )
        
        return GenerateResponse(
            success=True,
            response=response_text,
            confidence=0.9,
            model=groq_service.model
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"AI generation error: {e}")
        return GenerateResponse(
            success=False,
            response="Error generating response",
            error=str(e),
            confidence=0.0
        )


@router.get("/status")
async def get_ai_status():
    """
    Check AI service status
    
    Returns:
        Status information about Groq API
    """
    return groq_service.check_status()


class TeachFactRequest(BaseModel):
    """Request model for teaching the AI a new fact"""
    fact: str
    category: str = "other"  # logistics, products, regions, partners, other


class TeachFactResponse(BaseModel):
    """Response model for teach fact"""
    success: bool
    fact_id: str
    message: str


@router.post("/teach-fact", response_model=TeachFactResponse)
async def teach_fact(request: TeachFactRequest):
    """
    Teach the AI a new company fact
    
    Example: "В Гродно у нас теперь новый склад"
    
    Args:
        request: Fact to teach with optional category
        
    Returns:
        Success status and fact ID
    """
    try:
        new_fact = company_knowledge_service.add_fact(
            fact=request.fact,
            category=request.category,
            created_by="user"
        )
        
        return TeachFactResponse(
            success=True,
            fact_id=new_fact["id"],
            message=f"Факт успешно сохранён в категории '{request.category}'"
        )
    except Exception as e:
        logger.error(f"Failed to teach fact: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сохранения факта: {str(e)}"
        )


@router.get("/facts")
async def get_facts(category: Optional[str] = None):
    """
    Get all company facts or filter by category
    
    Args:
        category: Optional category filter
        
    Returns:
        List of facts
    """
    try:
        if category:
            facts = company_knowledge_service.get_facts_by_category(category)
        else:
            facts = company_knowledge_service.get_all_facts()
        
        return {
            "success": True,
            "count": len(facts),
            "facts": facts
        }
    except Exception as e:
        logger.error(f"Failed to get facts: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения фактов: {str(e)}"
        )


@router.get("/belarus-context")
async def get_belarus_context():
    """
    Get Belarus market context
    
    Returns:
        Belarus market information
    """
    try:
        context = company_knowledge_service.get_belarus_context()
        return {
            "success": True,
            "context": context
        }
    except Exception as e:
        logger.error(f"Failed to get Belarus context: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка получения контекста: {str(e)}"
        )
