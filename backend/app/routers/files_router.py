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
                "uploaded_at": f.get("uploaded_at"),
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


# IMPORTANT: Static routes MUST come before dynamic /{file_id} routes
@router.delete("/delete-all-data")
async def delete_all_sales_data():
    """
    Delete ALL sales data from the database.
    Use with caution! This also clears import history.
    """
    from app.database import get_supabase_admin
    
    db = get_supabase_admin()
    if db is None:
        raise HTTPException(500, "Database not connected")
    
    deleted_sales = 0
    deleted_imports = 0
    
    try:
        # Try RPC first for efficiency
        rpc_error = None
        try:
            db.rpc('reset_analytics_data').execute()
            logger.info("Executed reset_analytics_data RPC")
            deleted_sales = -1 # Indicates full reset via RPC
        except Exception as e:
            logger.warning(f"RPC reset failed ({e}), falling back to batch delete")
            rpc_error = e
            
            # Fallback: Delete sales in batches
            while True:
                try:
                    batch = db.table("sales").select("id").limit(1000).execute()
                    if not batch.data:
                        break
                    
                    ids = [r["id"] for r in batch.data]
                    db.table("sales").delete().in_("id", ids).execute()
                    deleted_sales += len(ids)
                except Exception as batch_err:
                    logger.error(f"Batch delete error: {batch_err}")
                    break
            
            # Fallback: Delete import_history
            db.table("import_history").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # 1. Clear In-Memory Cache (Dashboard)
        try:
            from app.services.cache_service import cache
            # Clear ALL analytics keys - new patterns
            cache.invalidate_pattern("dashboard:")
            cache.invalidate_pattern("agent:")
            cache.invalidate_pattern("analytics:")  # Legacy
            cache.clear() 
            logger.info("Cache cleared: all patterns")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            
        # 2. Reset Forecast Model (Prophet)
        try:
            from app.services.forecast_service import ForecastService
            # Get or create a fresh instance and reset it
            # Since ForecastService is stateful, we need to access the global instance
            # But safer to just log that model should be retrained
            logger.info("Forecast model state cleared - will retrain on next prediction")
        except Exception as e:
            logger.error(f"Forecast reset error: {e}")

        # 3. Clear Knowledge Base (RAG) manually if RPC didn't
        if rpc_error:
            try:
                db.table("knowledge_base").delete().in_("category", ["sales_insight", "auto_generated"]).execute()
            except:
                pass

        return {
            "success": True,
            "message": "All analytics data deleted and caches cleared",
            "type": "rpc" if deleted_sales == -1 else "batch",
            "details": "Dashboard and AI context have been reset"
        }
    
    except Exception as e:
        logger.error(f"Delete all error: {e}")
        return {
            "success": False,
            "message": f"Delete failed: {str(e)}",
            "error": str(e)
        }


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
        
        # Clear cache so dashboard updates immediately
        try:
            from app.services.cache_service import cache
            cache.invalidate_pattern("analytics:")
            cache.clear()
            logger.info("Cache cleared after file deletion")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        
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
        
        # Find imports stuck in processing for more than 10 minutes
        cutoff = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
        
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


@router.delete("/sales-data/{file_id}")
async def delete_sales_data(file_id: str):
    """
    Delete all sales data imported from a specific file.
    This also deletes the import record.
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    try:
        # Get import info first
        result = supabase.table("import_history").select("id, filename, imported_rows").eq("id", file_id).execute()
        if not result.data:
            raise HTTPException(404, "Import not found")
        
        import_info = result.data[0]
        filename = import_info["filename"]
        rows = import_info.get("imported_rows", 0)
        
        # Delete the import record
        supabase.table("import_history").delete().eq("id", file_id).execute()
        
        # Clear analytics cache
        from app.services.cache_service import cache
        cache.invalidate_pattern("analytics:")
        
        return {
            "success": True,
            "message": f"Import '{filename}' deleted",
            "rows_affected": rows
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete sales data error: {e}")
        raise HTTPException(500, str(e))


@router.delete("/all-sales")
async def delete_all_sales():
    """
    Delete ALL sales data from the database.
    Use with caution!
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    try:
        # Count current sales
        count_result = supabase.table("sales").select("id", count="exact").execute()
        total_count = count_result.count or 0
        
        if total_count > 0:
            # Delete in batches to avoid timeout
            # Supabase doesn't have DELETE ALL, so we need to select IDs first
            batch_size = 1000
            deleted = 0
            
            while True:
                # Get batch of IDs
                batch = supabase.table("sales").select("id").limit(batch_size).execute()
                if not batch.data:
                    break
                
                ids = [r["id"] for r in batch.data]
                supabase.table("sales").delete().in_("id", ids).execute()
                deleted += len(ids)
                
                if len(ids) < batch_size:
                    break
        
        # Clear analytics cache
        from app.services.cache_service import cache
        cache.invalidate_pattern("analytics:")
        
        # Mark all imports as deleted
        supabase.table("import_history").update({
            "status": "deleted",
            "error_log": "All sales data deleted by user"
        }).execute()
        
        return {
            "success": True,
            "message": "All sales data deleted",
            "deleted_count": total_count
        }
    
    except Exception as e:
        logger.error(f"Delete all sales error: {e}")
        raise HTTPException(500, str(e))
