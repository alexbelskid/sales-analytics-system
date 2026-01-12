from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import pandas as pd
import io
from uuid import uuid4
from datetime import datetime
from app.database import supabase
from app.services.analytics_service import AnalyticsService
from app.services.cache_service import cache
import logging

logger = logging.getLogger(__name__)

# SECURITY: File upload constraints
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}
ALLOWED_MIME_TYPES = {
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/octet-stream',  # Sometimes CSV files come with this
}


async def validate_upload_file(file: UploadFile) -> bytes:
    """
    Validate uploaded file for security.
    Returns file contents if valid, raises HTTPException otherwise.
    """
    # Check filename extension
    if not file.filename:
        raise HTTPException(400, "Filename is required")
    
    ext = '.' + file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            400, 
            f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check MIME type (if provided)
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Suspicious MIME type: {file.content_type} for file {file.filename}")
        # Don't reject outright, but log it
    
    # Read and check file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            400, 
            f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB"
        )
    
    if len(contents) == 0:
        raise HTTPException(400, "Empty file")
    
    return contents


router = APIRouter(prefix="/api/data", tags=["Data Integration"])


@router.post("/upload/sales")
async def upload_sales(
    file: UploadFile = File(...),
    mode: str = Form("append")  # 'append' or 'replace'
):
    """Upload sales CSV - Uses unified importer for consistent tracking"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        
        # Read file into DataFrame
        df = pd.read_csv(io.BytesIO(contents))
        
        # Validate required columns
        required_cols = ['date', 'customer_name', 'product_name', 'quantity', 'price', 'amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(400, f"Отсутствуют колонки: {missing_cols}")
        
        # Use unified importer
        from app.services.unified_importer import UnifiedImporter
        
        importer = UnifiedImporter()
        result = await importer.import_data(
            df=df,
            filename=file.filename,
            file_size=len(contents),
            data_type='sales',
            mode=mode
        )
        
        # Clear cache
        cache.clear_all()
        
        if not result.success:
            raise HTTPException(400, result.message)
        
        return {
            "success": True,
            "import_id": result.import_id,
            "rows_added": result.imported_rows,
            "rows_skipped": result.failed_rows,
            "mode": mode,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sales upload error: {e}")
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


@router.post("/upload/products")
async def upload_products(
    file: UploadFile = File(...),
    mode: str = Form("append")
):
    """Upload products CSV - Uses unified importer for consistent tracking"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        df = pd.read_csv(io.BytesIO(contents))
        
        # Use unified importer
        from app.services.unified_importer import UnifiedImporter
        
        importer = UnifiedImporter()
        result = await importer.import_data(
            df=df,
            filename=file.filename,
            file_size=len(contents),
            data_type='products',
            mode=mode
        )
        
        cache.clear_all()
        
        if not result.success:
            raise HTTPException(400, result.message)
        
        return {
            "success": True,
            "import_id": result.import_id,
            "rows_added": result.imported_rows,
            "mode": mode,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Products upload error: {e}")
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


@router.post("/upload/customers")
async def upload_customers(
    file: UploadFile = File(...),
    mode: str = Form("append")
):
    """Upload customers CSV - Uses unified importer for consistent tracking"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        df = pd.read_csv(io.BytesIO(contents))
        
        # Use unified importer
        from app.services.unified_importer import UnifiedImporter
        
        importer = UnifiedImporter()
        result = await importer.import_data(
            df=df,
            filename=file.filename,
            file_size=len(contents),
            data_type='customers',
            mode=mode
        )
        
        cache.clear_all()
        
        if not result.success:
            raise HTTPException(400, result.message)
        
        return {
            "success": True,
            "import_id": result.import_id,
            "rows_added": result.imported_rows,
            "mode": mode,
            "message": result.message
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Customers upload error: {e}")
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")

@router.get("/analytics/summary")
async def get_analytics_summary():
    """Summary of all analytics for Dashboard and AI"""
    service = AnalyticsService()
    return {
        "sales": service.get_sales_summary(),
        "clients": service.get_clients_summary(),
        "monthly": service.get_monthly_stats(),
        "knowledge": service.get_knowledge_stats(),
        "training": service.get_training_stats()
    }
