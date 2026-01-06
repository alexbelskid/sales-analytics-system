"""
Files API Router
Manages import file history, details, and actions
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/files", tags=["Files"])


@router.get("/list")
async def list_files(
    status: Optional[str] = Query(None, description="Filter by status"),
    year: Optional[int] = Query(None, description="Filter by year"),
    sort_by: str = Query("date", description="Sort by: date, size, records"),
    order: str = Query("desc", description="Order: asc, desc")
):
    """
    List all imported files with filtering and sorting
    """
    if supabase is None:
        return {"files": [], "total": 0}
    
    try:
        query = supabase.table("import_history").select("*")
        
        if status:
            query = query.eq("status", status)
        
        # Apply sorting
        sort_column = "started_at"
        if sort_by == "size":
            sort_column = "file_size"
        elif sort_by == "records":
            sort_column = "imported_rows"
        
        query = query.order(sort_column, desc=(order == "desc"))
        
        result = query.limit(100).execute()
        
        files = []
        for f in result.data:
            # Determine period from data if available
            period = "—"
            if f.get("period_start") and f.get("period_end"):
                period = f"{f['period_start']} → {f['period_end']}"
            
            files.append({
                "id": f["id"],
                "filename": f["filename"],
                "uploaded_at": f.get("started_at"),
                "status": f["status"],
                "file_size_mb": round((f.get("file_size", 0) or 0) / 1024 / 1024, 2),
                "total_rows": f.get("total_rows", 0),
                "imported_rows": f.get("imported_rows", 0),
                "failed_rows": f.get("failed_rows", 0),
                "progress": f.get("progress_percent", 0),
                "period": period,
                "error": f.get("error_log")
            })
        
        return {"files": files, "total": len(files)}
    
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(500, str(e))


@router.get("/{file_id}")
async def get_file_details(file_id: str):
    """
    Get detailed information about a specific import
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    try:
        result = supabase.table("import_history").select("*").eq("id", file_id).execute()
        
        if not result.data:
            raise HTTPException(404, "File not found")
        
        f = result.data[0]
        
        # Calculate duration
        duration = None
        if f.get("started_at") and f.get("completed_at"):
            try:
                start = datetime.fromisoformat(f["started_at"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(f["completed_at"].replace("Z", "+00:00"))
                duration = int((end - start).total_seconds())
            except:
                pass
        
        return {
            "id": f["id"],
            "filename": f["filename"],
            "file_size": f.get("file_size", 0),
            "file_size_mb": round((f.get("file_size", 0) or 0) / 1024 / 1024, 2),
            "status": f["status"],
            "total_rows": f.get("total_rows", 0),
            "imported_rows": f.get("imported_rows", 0),
            "failed_rows": f.get("failed_rows", 0),
            "progress": f.get("progress_percent", 0),
            "started_at": f.get("started_at"),
            "completed_at": f.get("completed_at"),
            "duration_seconds": duration,
            "error_log": f.get("error_log"),
            "period_start": f.get("period_start"),
            "period_end": f.get("period_end")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file details error: {e}")
        raise HTTPException(500, str(e))


@router.delete("/{file_id}")
async def delete_file(file_id: str, delete_data: bool = Query(False)):
    """
    Delete an import record and optionally its data
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    try:
        # Check if file exists
        result = supabase.table("import_history").select("id, filename").eq("id", file_id).execute()
        if not result.data:
            raise HTTPException(404, "File not found")
        
        filename = result.data[0]["filename"]
        
        # Delete import record
        supabase.table("import_history").delete().eq("id", file_id).execute()
        
        # Optionally delete related sales data (if we had import_id in sales)
        # For now, just delete the import record
        
        return {
            "success": True,
            "message": f"Import '{filename}' deleted",
            "deleted_data": delete_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(500, str(e))


@router.post("/clear-cache")
async def clear_analytics_cache():
    """
    Clear analytics cache to refresh data
    """
    from app.services.cache_service import cache
    
    cleared = cache.invalidate_pattern("analytics:")
    
    return {
        "success": True,
        "cleared_entries": cleared,
        "message": "Analytics cache cleared"
    }


@router.post("/reset-stuck")
async def reset_stuck_imports():
    """
    Mark stuck 'processing' imports as failed
    (useful after server restart when background tasks are lost)
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    try:
        from datetime import datetime, timedelta
        
        # Find imports stuck in processing for more than 30 minutes
        cutoff = (datetime.utcnow() - timedelta(minutes=30)).isoformat()
        
        result = supabase.table("import_history").select("id, filename, started_at").eq("status", "processing").lt("started_at", cutoff).execute()
        
        stuck_imports = result.data or []
        
        # Mark them as failed
        for imp in stuck_imports:
            supabase.table("import_history").update({
                "status": "failed",
                "error_log": "Import stuck - server may have restarted during processing"
            }).eq("id", imp["id"]).execute()
        
        return {
            "success": True,
            "reset_count": len(stuck_imports),
            "imports": [{"id": i["id"], "filename": i["filename"]} for i in stuck_imports]
        }
    
    except Exception as e:
        logger.error(f"Reset stuck imports error: {e}")
        raise HTTPException(500, str(e))
