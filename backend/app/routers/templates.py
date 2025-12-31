from fastapi import APIRouter, HTTPException
from typing import List
from app.database import supabase
from app.models.email import Template, TemplateCreate

router = APIRouter()

@router.get("/", response_model=List[Template])
async def get_templates():
    """Get all templates"""
    if not supabase:
        return []
    try:
        result = supabase.table("response_templates").select("*").order("usage_count", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Template)
async def create_template(template: TemplateCreate):
    """Create new template"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        data = template.dict()
        result = supabase.table("response_templates").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{template_id}", response_model=Template)
async def update_template(template_id: str, template: TemplateCreate):
    """Update template"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        data = template.dict(exclude_unset=True)
        result = supabase.table("response_templates").update(data).eq("id", template_id).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{template_id}")
async def delete_template(template_id: str):
    """Delete template"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        supabase.table("response_templates").delete().eq("id", template_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
