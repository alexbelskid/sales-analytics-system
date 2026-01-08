"""
Knowledge Base Router
CRUD operations for company knowledge base (products, terms, contacts, FAQ, company info)
Uses direct PostgreSQL connection to bypass PostgREST schema cache issues
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from app import db_direct

logger = logging.getLogger(__name__)

router = APIRouter()


class KnowledgeItem(BaseModel):
    """Knowledge base item model"""
    id: Optional[str] = None
    category: str  # products, terms, contacts, faq, company_info
    title: str
    content: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class KnowledgeCreate(BaseModel):
    """Create knowledge base item"""
    category: str
    title: str
    content: str


class KnowledgeUpdate(BaseModel):
    """Update knowledge base item"""
    category: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None


VALID_CATEGORIES = ["products", "terms", "contacts", "faq", "company_info"]


@router.get("", response_model=List[KnowledgeItem])
async def list_knowledge(category: Optional[str] = None):
    """List all knowledge base items, optionally filtered by category"""
    try:
        items = db_direct.get_all_knowledge(category)
        return items
    except Exception as e:
        logger.error(f"Error listing knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=KnowledgeItem)
async def get_knowledge(item_id: str):
    """Get single knowledge base item by ID"""
    try:
        item = db_direct.get_knowledge_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=KnowledgeItem)
async def create_knowledge(item: KnowledgeCreate):
    """Create new knowledge base item"""
    try:
        # Validate category
        if item.category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
            )
        
        result = db_direct.insert_knowledge(item.category, item.title, item.content)
        logger.info(f"Created knowledge item: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=KnowledgeItem)
async def update_knowledge(item_id: str, item: KnowledgeUpdate):
    """Update existing knowledge base item"""
    try:
        if item.category and item.category not in VALID_CATEGORIES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}"
            )
        
        result = db_direct.update_knowledge(
            item_id,
            category=item.category,
            title=item.title,
            content=item.content
        )
        
        if not result:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def delete_knowledge(item_id: str):
    """Delete knowledge base item"""
    try:
        success = db_direct.delete_knowledge(item_id)
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        return {"success": True, "message": "Knowledge item deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        items = db_direct.get_all_knowledge()
        
        # Count by category
        categories = {}
        for item in items:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total": len(items),
            "by_category": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
