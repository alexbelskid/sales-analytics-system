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
    """Upload sales CSV"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        df = pd.read_csv(io.BytesIO(contents))
        
        required_cols = ['date', 'customer_name', 'product_name', 'quantity', 'price', 'amount']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise HTTPException(400, f"Отсутствуют колонки: {missing_cols}")
        
        if mode == "replace":
            # Delete order matters due to FK
            supabase.table("sale_items").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            supabase.table("sales").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        rows_added = 0
        rows_skipped = 0
        
        for _, row in df.iterrows():
            try:
                # Get or create customer
                c_res = supabase.table("customers").select("id").eq("name", row['customer_name']).execute()
                if c_res.data:
                    customer_id = c_res.data[0]["id"]
                else:
                    new_c = supabase.table("customers").insert({"name": row['customer_name']}).execute()
                    customer_id = new_c.data[0]["id"]
                
                # Get or create product
                p_res = supabase.table("products").select("id").eq("name", row['product_name']).execute()
                if p_res.data:
                    product_id = p_res.data[0]["id"]
                else:
                    new_p = supabase.table("products").insert({
                        "name": row['product_name'],
                        "price": float(row['price'])
                    }).execute()
                    product_id = new_p.data[0]["id"]
                
                # Append mode: check for duplicate
                sale_date = pd.to_datetime(row['date']).date().isoformat()
                if mode == "append":
                    # Simple check: same customer, same date, same amount
                    existing = supabase.table("sales").select("id").eq("customer_id", customer_id).eq("sale_date", sale_date).eq("total_amount", float(row['amount'])).execute()
                    if existing.data:
                        rows_skipped += 1
                        continue
                
                # Create sale
                sale_res = supabase.table("sales").insert({
                    "date": sale_date, # Some tables might use 'sale_date', some 'date'
                    "sale_date": sale_date,
                    "customer_id": customer_id,
                    "total_amount": float(row['amount'])
                }).execute()
                sale_id = sale_res.data[0]["id"]
                
                # Create sale item
                supabase.table("sale_items").insert({
                    "sale_id": sale_id,
                    "product_id": product_id,
                    "quantity": float(row['quantity']),
                    "price": float(row['price']),
                    "unit_price": float(row['price']),
                    "amount": float(row['amount'])
                }).execute()
                
                rows_added += 1
            except Exception as e:
                print(f"Row skip error: {e}")
                continue
                
        # Invalidate cache after upload
        cache.invalidate_pattern("analytics:")
        
        return {"success": True, "rows_added": rows_added, "rows_skipped": rows_skipped, "mode": mode}
    except Exception as e:
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")

@router.post("/upload/products")
async def upload_products(
    file: UploadFile = File(...),
    mode: str = Form("append")
):
    """Upload products CSV"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        df = pd.read_csv(io.BytesIO(contents))
        
        if mode == "replace":
            supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
        rows_added = 0
        for _, row in df.iterrows():
            if mode == "append":
                existing = supabase.table("products").select("id").eq("name", row['name']).execute()
                if existing.data:
                    continue
            
            supabase.table("products").insert({
                "name": row['name'],
                "category": row.get('category'),
                "price": float(row.get('price', 0))
            }).execute()
            rows_added += 1
            
        return {"success": True, "rows_added": rows_added, "mode": mode}
    except Exception as e:
        raise HTTPException(500, f"Ошибка: {str(e)}")

@router.post("/upload/customers")
async def upload_customers(
    file: UploadFile = File(...),
    mode: str = Form("append")
):
    """Upload customers CSV"""
    try:
        # SECURITY: Validate file before processing
        contents = await validate_upload_file(file)
        df = pd.read_csv(io.BytesIO(contents))
        
        if mode == "replace":
            supabase.table("customers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
        rows_added = 0
        for _, row in df.iterrows():
            if mode == "append":
                existing = supabase.table("customers").select("id").eq("name", row['name']).execute()
                if existing.data:
                    continue
            
            supabase.table("customers").insert({
                "name": row['name'],
                "email": row.get('email'),
                "phone": row.get('phone')
            }).execute()
            rows_added += 1
            
        return {"success": True, "rows_added": rows_added, "mode": mode}
    except Exception as e:
        raise HTTPException(500, f"Ошибка: {str(e)}")

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
