"""
Import API Router
Handles Excel file uploads and import operations
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import Optional
import tempfile
import os
import logging
from app.services.import_service import ImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/import", tags=["Import"])

# Store active imports for background task tracking
active_imports: dict = {}


@router.post("/upload-excel")
async def upload_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload and import Excel file
    
    - Accepts Excel files up to 100 MB
    - Saves temporarily and starts background import
    - Returns import_id for status tracking
    """
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(400, "Только Excel файлы (.xlsx, .xls)")
    
    # Check file size (100 MB limit)
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > 100 * 1024 * 1024:  # 100 MB
        raise HTTPException(400, "Файл слишком большой (макс. 100 МБ)")
    
    try:
        # Save to temp file
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, file.filename)
        
        with open(temp_path, 'wb') as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved upload: {file.filename} ({file_size} bytes)")
        
        # Create import service and get import ID
        service = ImportService()
        
        # Create import record first to get ID
        from app.database import supabase
        import_result = supabase.table('import_history').insert({
            'filename': file.filename,
            'file_size': file_size,
            'status': 'pending'
        }).execute()
        
        import_id = import_result.data[0]['id']
        
        # Run import in background
        background_tasks.add_task(
            run_import_background,
            import_id,
            temp_path,
            file.filename,
            file_size,
            temp_dir
        )
        
        return {
            'success': True,
            'message': 'Импорт запущен в фоновом режиме',
            'import_id': import_id,
            'filename': file.filename,
            'file_size': file_size
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(500, f"Ошибка загрузки: {str(e)}")


async def run_import_background(
    import_id: str,
    file_path: str,
    filename: str,
    file_size: int,
    temp_dir: str
):
    """Background task for import processing"""
    try:
        from app.services.excel_parser import ExcelParser
        from app.services.import_service import ImportService
        from app.database import get_supabase_admin
        from datetime import datetime
        
        # Use admin client to bypass RLS
        supabase = get_supabase_admin()
        if not supabase:
            raise Exception("Database not configured")
        
        logger.info(f"Starting background import: {import_id}")
        
        # Update status to processing
        supabase.table('import_history').update({
            'status': 'processing',
            'started_at': datetime.now().isoformat()
        }).eq('id', import_id).execute()
        
        # Initialize parser and count rows
        parser = ExcelParser(file_path, chunk_size=5000)
        total_rows = parser.count_rows()
        
        supabase.table('import_history').update({
            'total_rows': total_rows
        }).eq('id', import_id).execute()
        
        # Pre-load caches
        customers_cache = {}
        products_cache = {}
        stores_cache = {}
        
        # Load existing entities
        result = supabase.table('customers').select('id, normalized_name').execute()
        for c in result.data:
            customers_cache[c['normalized_name']] = c['id']
        
        result = supabase.table('products').select('id, normalized_name').execute()
        for p in result.data:
            products_cache[p['normalized_name']] = p['id']
        
        result = supabase.table('stores').select('id, code').execute()
        for s in result.data:
            if s['code']:
                stores_cache[s['code']] = s['id']
        
        imported_rows = 0
        failed_rows = 0
        sales_batch = []
        
        # Process chunks
        for chunk in parser.parse_chunks():
            for row_data in chunk:
                try:
                    # Get or create customer
                    normalized_customer = row_data['customer_name']
                    if normalized_customer not in customers_cache:
                        result = supabase.table('customers').insert({
                            'name': row_data['customer_raw'],
                            'normalized_name': normalized_customer
                        }).execute()
                        customers_cache[normalized_customer] = result.data[0]['id']
                    customer_id = customers_cache[normalized_customer]
                    
                    # Get or create product
                    normalized_product = row_data['product_name']
                    if normalized_product not in products_cache:
                        result = supabase.table('products').insert({
                            'name': row_data['product_raw'],
                            'normalized_name': normalized_product,
                            'category': row_data.get('category', 'Без категории')
                        }).execute()
                        products_cache[normalized_product] = result.data[0]['id']
                    product_id = products_cache[normalized_product]
                    
                    # Get or create store
                    store_id = None
                    store_code = row_data.get('store_code')
                    if store_code:
                        store_code = str(store_code)
                        if store_code not in stores_cache:
                            result = supabase.table('stores').insert({
                                'code': store_code,
                                'name': row_data.get('store_name') or store_code,
                                'region': row_data.get('region'),
                                'channel': row_data.get('channel')
                            }).execute()
                            stores_cache[store_code] = result.data[0]['id']
                        store_id = stores_cache[store_code]
                    
                    # Add to sales batch
                    sales_batch.append({
                        'sale_date': row_data['sale_date'].isoformat(),
                        'customer_id': customer_id,
                        'store_id': store_id,
                        'total_amount': row_data['amount'],
                        'year': row_data['year'],
                        'month': row_data['month'],
                        'week': row_data['week'],
                        'day_of_week': row_data['day_of_week']
                    })
                    imported_rows += 1
                    
                    # Batch insert
                    if len(sales_batch) >= 1000:
                        supabase.table('sales').insert(sales_batch).execute()
                        sales_batch = []
                        
                        # Update progress
                        progress = int((imported_rows / max(total_rows, 1)) * 100)
                        supabase.table('import_history').update({
                            'imported_rows': imported_rows,
                            'progress_percent': progress
                        }).eq('id', import_id).execute()
                        
                        logger.info(f"Import progress: {imported_rows}/{total_rows} ({progress}%)")
                
                except Exception as e:
                    failed_rows += 1
                    logger.error(f"Row error: {e}")
        
        # Insert remaining
        if sales_batch:
            supabase.table('sales').insert(sales_batch).execute()
        
        # Mark complete
        supabase.table('import_history').update({
            'status': 'completed',
            'imported_rows': imported_rows,
            'failed_rows': failed_rows,
            'progress_percent': 100,
            'completed_at': datetime.now().isoformat()
        }).eq('id', import_id).execute()
        
        # Invalidate cache
        from app.services.cache_service import cache
        cache.invalidate_pattern("analytics:")
        
        logger.info(f"Import complete: {imported_rows} rows, {failed_rows} failed")
        
    except Exception as e:
        logger.error(f"Background import error: {e}")
        supabase.table('import_history').update({
            'status': 'failed',
            'error_log': str(e)
        }).eq('id', import_id).execute()
    
    finally:
        # Cleanup temp files
        try:
            os.remove(file_path)
            os.rmdir(temp_dir)
        except:
            pass


@router.get("/status/{import_id}")
async def get_import_status(import_id: str):
    """
    Get import status and progress
    
    Returns:
    - status: pending/processing/completed/failed
    - progress_percent: 0-100
    - imported_rows / total_rows
    - errors if any
    """
    status = await ImportService.get_import_status(import_id)
    
    if not status:
        raise HTTPException(404, "Импорт не найден")
    
    return status


@router.get("/history")
async def get_import_history(limit: int = 20):
    """
    Get recent import history
    """
    history = await ImportService.get_import_history(limit)
    return {'imports': history}
