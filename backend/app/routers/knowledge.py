"""
Knowledge Base Router
CRUD operations for company knowledge base (products, terms, contacts, FAQ, company info)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import logging

from app.database import get_supabase

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


@router.get("", response_model=List[KnowledgeItem])
async def list_knowledge(category: Optional[str] = None):
    """
    List all knowledge base items, optionally filtered by category
    
    Args:
        category: Filter by category (products, terms, contacts, faq, company_info)
    """
    try:
        supabase = get_supabase()
        
        query = supabase.table("knowledge_base").select("*")
        
        if category:
            query = query.eq("category", category)
        
        response = query.order("created_at", desc=True).execute()
        
        return response.data
        
    except Exception as e:
        logger.error(f"Error listing knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{item_id}", response_model=KnowledgeItem)
async def get_knowledge(item_id: str):
    """Get single knowledge base item by ID"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("knowledge_base").select("*").eq("id", item_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=KnowledgeItem)
async def create_knowledge(item: KnowledgeCreate):
    """Create new knowledge base item"""
    try:
        supabase = get_supabase()
        
        # Validate category
        valid_categories = ["products", "terms", "contacts", "faq", "company_info"]
        if item.category not in valid_categories:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
            )
        
        data = {
            "category": item.category,
            "title": item.title,
            "content": item.content
        }
        
        response = supabase.table("knowledge_base").insert(data).execute()
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{item_id}", response_model=KnowledgeItem)
async def update_knowledge(item_id: str, item: KnowledgeUpdate):
    """Update existing knowledge base item"""
    try:
        supabase = get_supabase()
        
        # Build update data
        update_data = {}
        if item.category is not None:
            valid_categories = ["products", "terms", "contacts", "faq", "company_info"]
            if item.category not in valid_categories:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
                )
            update_data["category"] = item.category
        if item.title is not None:
            update_data["title"] = item.title
        if item.content is not None:
            update_data["content"] = item.content
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        response = supabase.table("knowledge_base").update(update_data).eq("id", item_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return response.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{item_id}")
async def delete_knowledge(item_id: str):
    """Delete knowledge base item"""
    try:
        supabase = get_supabase()
        
        response = supabase.table("knowledge_base").delete().eq("id", item_id).execute()
        
        if not response.data:
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
        supabase = get_supabase()
        
        response = supabase.table("knowledge_base").select("category").execute()
        
        # Count by category
        categories = {}
        for item in response.data:
            cat = item["category"]
            categories[cat] = categories.get(cat, 0) + 1
        
        return {
            "total": len(response.data),
            "by_category": categories
        }
        
    except Exception as e:
        logger.error(f"Error getting knowledge stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
