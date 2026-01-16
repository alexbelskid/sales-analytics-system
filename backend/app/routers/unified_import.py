"""
Unified Import Router
Single endpoint for all data uploads with automatic type detection
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import date
import pandas as pd
import tempfile
import os
import logging

from app.services.unified_importer import UnifiedImporter, ImportResult

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["Unified Import"])


@router.post("/unified")
async def unified_upload(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    data_type: Optional[str] = Form(None),
    mode: str = Form("append"),
    period_start: Optional[str] = Form(None),
    period_end: Optional[str] = Form(None)
):
    """
    Unified upload endpoint for all data types
    
    - **file**: Excel or CSV file
    - **data_type**: Optional explicit type (sales, agents, customers, products). Auto-detected if not provided
    - **mode**: append or replace (default: append)
    - **period_start**: For agent data (YYYY-MM-DD format)
    - **period_end**: For agent data (YYYY-MM-DD format)
    """
    temp_path = None
    
    try:
        # Validate file type
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only Excel (.xlsx, .xls) and CSV (.csv) files are supported."
            )
        
        # Validate mode
        if mode not in ["append", "replace"]:
            raise HTTPException(status_code=400, detail="Mode must be 'append' or 'replace'")
        
        # Validate data_type if provided
        if data_type and data_type not in ["sales", "agents", "customers", "products"]:
            raise HTTPException(
                status_code=400,
                detail="data_type must be one of: sales, agents, customers, products"
            )
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
            file_size = len(content)
        
        # Validate file size before processing - max 50MB
        MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
        if file_size > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large ({file_size} bytes). Maximum allowed: 50MB"
            )
        
        # Read file into DataFrame
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_path)
        else:
            df = pd.read_excel(temp_path)
        
        logger.info(f"Loaded file {file.filename} with {len(df)} rows and columns: {df.columns.tolist()}")
        
        # Parse period dates if provided
        period_start_date = None
        period_end_date = None
        if period_start:
            try:
                period_start_date = date.fromisoformat(period_start)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid period_start format. Use YYYY-MM-DD")
        
        if period_end:
            try:
                period_end_date = date.fromisoformat(period_end)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid period_end format. Use YYYY-MM-DD")
        
        # Import data
        importer = UnifiedImporter()
        result: ImportResult = await importer.import_data(
            df=df,
            filename=file.filename,
            file_size=file_size,
            data_type=data_type,
            mode=mode,
            period_start=period_start_date,
            period_end=period_end_date
        )
        
        if not result.success:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "import_id": result.import_id,
                    "data_type": result.data_type,
                    "imported_rows": result.imported_rows,
                    "failed_rows": result.failed_rows,
                    "errors": result.errors,
                    "message": result.message
                }
            )
        
        return {
            "success": True,
            "import_id": result.import_id,
            "data_type": result.data_type,
            "imported_rows": result.imported_rows,
            "failed_rows": result.failed_rows,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    finally:
        # GUARANTEED cleanup of temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.info(f"Cleaned up temp file: {temp_path}")
            except Exception as cleanup_error:
                logger.error(f"Failed to cleanup temp file {temp_path}: {cleanup_error}")


@router.get("/types")
async def get_supported_types():
    """Get list of supported data types"""
    return {
        "types": [
            {
                "id": "sales",
                "name": "Sales",
                "description": "Sales transactions with customers and products",
                "required_columns": ["customer_name", "product_name", "quantity", "price", "date"]
            },
            {
                "id": "agents",
                "name": "Agents",
                "description": "Agent sales data with regions and brands",
                "required_columns": ["region", "user/agent", "brand", "plan", "sales"]
            },
            {
                "id": "customers",
                "name": "Customers",
                "description": "Customer contact information",
                "required_columns": ["name", "email", "phone"]
            },
            {
                "id": "products",
                "name": "Products",
                "description": "Product catalog with prices",
                "required_columns": ["name", "sku", "price", "category"]
            }
        ]
    }


@router.post("/detect-type")
async def detect_data_type(file: UploadFile = File(...)):
    """
    Detect data type from uploaded file without importing
    Useful for preview/confirmation before actual import
    """
    temp_path = None
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_path = tmp.name
        
        # Read file
        if file.filename.endswith('.csv'):
            df = pd.read_csv(temp_path)
        else:
            df = pd.read_excel(temp_path)
        
        # Detect type
        detected_type = UnifiedImporter.detect_data_type(df)
        
        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        return {
            "filename": file.filename,
            "detected_type": detected_type,
            "row_count": len(df),
            "columns": df.columns.tolist(),
            "preview": df.head(5).to_dict(orient='records')
        }
    
    except Exception as e:
        logger.error(f"Detection error: {e}")
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
        
        raise HTTPException(status_code=500, detail=f"Type detection failed: {str(e)}")
