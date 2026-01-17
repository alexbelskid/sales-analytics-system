"""
Intelligent Chat Router
API endpoints for the "AI-Intellect Core"
"""

from fastapi import APIRouter, HTTPException, Request, Body, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.services.unified_intelligence_service import unified_intelligence_service
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = False  # Future support for streaming

class SourceInfo(BaseModel):
    type: str
    status: str
    details: Any

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[SourceInfo]
    classification: Optional[Dict[str, Any]] = None

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat(request: Request, body: ChatRequest):
    """
    Unified Intelligence Chat Endpoint.
    Automatically routes query to Internal DB, Web Search, or Hybrid.
    """
    try:
        result = await unified_intelligence_service.process_message(
            body.session_id, 
            body.message
        )
        
        return ChatResponse(
            response=result["response"],
            session_id=result["session_id"],
            sources=result["sources"],
            classification=result.get("classification")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history/{session_id}")
async def get_history(session_id: str):
    """Retrieve conversation history for a session"""
    # Exposing the internal history for debugging/UI sync
    # In a real app, this should be paginated and from DB
    return unified_intelligence_service._get_history(session_id)

@router.delete("/chat/session/{session_id}")
async def clear_session(session_id: str):
    """Clear conversation history"""
    if session_id in unified_intelligence_service.conversation_history:
        del unified_intelligence_service.conversation_history[session_id]
        return {"success": True, "message": "Session cleared"}
    raise HTTPException(status_code=404, detail="Session not found")
