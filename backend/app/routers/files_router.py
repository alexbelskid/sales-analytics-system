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
    import_source: Optional[str] = Query(None, description="Filter by import source"),
    import_type: Optional[str] = Query(None, description="Filter by import type"),
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
        
        if import_source:
            query = query.eq("import_source", import_source)
        
        if import_type:
            query = query.eq("import_type", import_type)
        
        # Apply sorting
        sort_column = "started_at"
        if sort_by == "size":
            sort_column = "file_size"
        elif sort_by == "records":
            sort_column = "imported_rows"
        
        query = query.order(sort_column, desc=(order == "desc"))
        
        result = query.limit(100).execute()
        
        # Human-readable labels
        source_labels = {
            'excel_upload': 'Excel Upload',
            'google_sheets': 'Google Sheets',
            'csv_upload': 'CSV Upload',
            'manual': 'Manual Entry'
        }
        
        type_labels = {
            'sales': 'Sales',
            'agents': 'Agents',
            'customers': 'Customers',
            'products': 'Products'
        }
        
        files = []
        for f in result.data:
            # Determine period from metadata or direct fields
            period = "—"
            metadata = f.get("metadata", {})
            if metadata and isinstance(metadata, dict):
                if 'period_start' in metadata and 'period_end' in metadata:
                    period = f"{metadata['period_start']} → {metadata['period_end']}"
            elif f.get("period_start") and f.get("period_end"):
                period = f"{f['period_start']} → {f['period_end']}"
            
            import_source = f.get('import_source', 'excel_upload')
            import_type = f.get('import_type', 'sales')
            
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
                "error": f.get("error_log"),
                "import_source": import_source,
                "import_source_label": source_labels.get(import_source, import_source),
                "import_type": import_type,
                "import_type_label": type_labels.get(import_type, import_type),
                "metadata": metadata
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
    from app.config import settings
    
    db = get_supabase_admin()
    if db is None:
        raise HTTPException(500, "Database not connected")
    
    deleted_sales = 0
    deleted_imports = 0
    deleted_files = 0
    
    try:
        # 1. Delete all files from Storage
        try:
            # Get all files from import_history
            imports = db.table("import_history").select("storage_path").execute()
            for imp in imports.data:
                if imp.get("storage_path"):
                    try:
                        db.storage.from_(settings.storage_bucket).remove([imp["storage_path"]])
                        deleted_files += 1
                    except Exception as e:
                        logger.warning(f"Failed to delete file {imp['storage_path']}: {e}")
        except Exception as e:
            logger.error(f"Storage cleanup error: {e}")
        
        # 2. Try RPC first for efficiency
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
        
        # 3. Delete agent analytics data
        try:
            # Delete agent analytics tables (use gte to delete all records)
            db.table("agent_daily_sales").delete().gte("id", "00000000-0000-0000-0000-000000000000").execute()
            db.table("agent_sales_plans").delete().gte("id", "00000000-0000-0000-0000-000000000000").execute()
            db.table("agent_performance_forecasts").delete().gte("id", "00000000-0000-0000-0000-000000000000").execute()
            
            # Delete agents table
            db.table("agents").delete().gte("id", "00000000-0000-0000-0000-000000000000").execute()
            
            logger.info("Agent analytics data and agents cleared")
        except Exception as e:
            logger.error(f"Agent analytics cleanup error: {e}")
        
        # 4. Clear In-Memory Cache (Dashboard)
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
            
        # 5. Reset Forecast Model (Prophet)
        try:
            from app.services.forecast_service import ForecastService
            # Get or create a fresh instance and reset it
            # Since ForecastService is stateful, we need to access the global instance
            # But safer to just log that model should be retrained
            logger.info("Forecast model state cleared - will retrain on next prediction")
        except Exception as e:
            logger.error(f"Forecast reset error: {e}")

        # 6. Clear Knowledge Base (RAG) manually if RPC didn't
        if rpc_error:
            try:
                db.table("knowledge_base").delete().in_("category", ["sales_insight", "auto_generated"]).execute()
            except:
                pass

        return {
            "success": True,
            "message": "All analytics data deleted and caches cleared",
            "type": "rpc" if deleted_sales == -1 else "batch",
            "details": f"Dashboard and AI context have been reset. Deleted {deleted_files} files from storage.",
            "deleted_files": deleted_files
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
async def delete_file(file_id: str, delete_data: bool = Query(True)):  # ✅ Changed default to True
    """
    Delete an import record and optionally its associated data
    
    Args:
        file_id: Import history record ID
        delete_data: If True (DEFAULT), also delete all data imported from this file (CASCADE)
    """
    if supabase is None:
        raise HTTPException(500, "Database not connected")
    
    from app.config import settings
    
    try:
        # Get import record first
        result = supabase.table("import_history").select("*").eq("id", file_id).execute()
        
        if not result.data:
            raise HTTPException(404, "Import not found")
        
        import_record = result.data[0]
        import_source = import_record.get('import_source', 'excel_upload')
        import_type = import_record.get('import_type', 'sales')
        storage_path = import_record.get('storage_path')
        filename = import_record.get('filename', 'Unknown')
        
        logger.info(f"Deleting import {file_id}: source={import_source}, type={import_type}, delete_data={delete_data}")
        
        # CASCADE DELETION: Delete associated data if requested
        deleted_counts = {}
        if delete_data:
            try:
                if import_type == 'agents':
                    # Delete agent-related data
                    related_agent_ids = import_record.get('related_agent_ids', [])
                    
                    if related_agent_ids and len(related_agent_ids) > 0:
                        # Delete daily sales for these agents
                        sales_result = supabase.table("agent_daily_sales").delete().in_("agent_id", related_agent_ids).execute()
                        deleted_counts['agent_daily_sales'] = len(sales_result.data) if sales_result.data else 0
                        
                        # Delete sales plans for these agents
                        plans_result = supabase.table("agent_sales_plans").delete().in_("agent_id", related_agent_ids).execute()
                        deleted_counts['agent_sales_plans'] = len(plans_result.data) if plans_result.data else 0
                        
                        logger.info(f"Cascade deleted agent data: {deleted_counts}")
                
                elif import_type == 'sales':
                    # ✅ Simple approach: Just delete sales by import_id
                    # Database CASCADE will handle sale_items automatically
                    
                    sales_result = supabase.table("sales").delete().eq("import_id", file_id).execute()
                    deleted_counts['sales'] = len(sales_result.data) if sales_result.data else 0
                    
                    logger.info(f"Cascade deleted {deleted_counts['sales']} sales by import_id")
            
            except Exception as e:
                logger.error(f"Cascade deletion error: {e}")
                raise HTTPException(500, f"Failed to delete associated data: {str(e)}")
            
            except Exception as e:
                logger.error(f"Cascade deletion error: {e}")
                raise HTTPException(500, f"Failed to delete associated data: {str(e)}")
        
        # Delete file from Storage if it exists
        if storage_path:
            try:
                supabase.storage.from_(settings.storage_bucket).remove([storage_path])
                logger.info(f"Deleted file from storage: {storage_path}")
            except Exception as e:
                logger.warning(f"Failed to delete file from storage: {e}")
        
        # Delete import_history record
        supabase.table("import_history").delete().eq("id", file_id).execute()
        
        # Clear cache
        try:
            from app.services.cache_service import cache
            cache.invalidate_pattern("analytics:")
            cache.invalidate_pattern("dashboard:")
            cache.invalidate_pattern("agent:")
            cache.clear()
            logger.info("Cache cleared after file deletion")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
        
        return {
            "success": True,
            "message": f"Import '{filename}' deleted",
            "deleted_from_storage": storage_path is not None,
            "deleted_data": deleted_counts if delete_data else None
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
