from fastapi import APIRouter, HTTPException, Body
from typing import List
from app.database import supabase
from app.models.email import ToneSetting, ToneSettingCreate

router = APIRouter()

@router.get("/", response_model=List[ToneSetting])
async def get_tone_settings():
    """Get all available tone presets"""
    if not supabase:
        return []
    try:
        # Order by system tones first, then user created
        result = supabase.table("response_tone_settings").select("*").order("is_system", desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=ToneSetting)
async def create_tone_setting(tone: ToneSettingCreate):
    """Create new custom tone"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        data = tone.dict()
        data["is_system"] = False # User created
        result = supabase.table("response_tone_settings").insert(data).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{tone_id}", response_model=ToneSetting)
async def update_tone_setting(tone_id: str, tone: ToneSettingCreate):
    """Update existing tone"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        data = tone.dict(exclude_unset=True)
        result = supabase.table("response_tone_settings").update(data).eq("id", tone_id).execute()
        return result.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tone_id}")
async def delete_tone_setting(tone_id: str):
    """Delete custom tone"""
    if not supabase:
        raise HTTPException(status_code=503, detail="Database not configured")
    try:
        # Prevent deleting system tones
        check = supabase.table("response_tone_settings").select("is_system").eq("id", tone_id).single().execute()
        if check.data and check.data.get("is_system"):
             raise HTTPException(status_code=400, detail="Cannot delete system presets")
             
        supabase.table("response_tone_settings").delete().eq("id", tone_id).execute()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
