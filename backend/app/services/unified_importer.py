"""
Unified Import Service
Handles all data imports (Sales, Agents, Customers, Products) through a single interface
with consistent import_history tracking
"""

from typing import Optional, Dict, Any, List
import pandas as pd
from datetime import datetime, date
from uuid import uuid4
import logging

from app.database import supabase_admin as supabase
from app.services.google_sheets_importer import GoogleSheetsImporter

logger = logging.getLogger(__name__)


class ImportResult:
    """Result of an import operation"""
    def __init__(
        self,
        success: bool,
        import_id: Optional[str] = None,
        data_type: str = "unknown",
        imported_rows: int = 0,
        failed_rows: int = 0,
        errors: List[str] = None,
        message: str = ""
    ):
        self.success = success
        self.import_id = import_id
        self.data_type = data_type
        self.imported_rows = imported_rows
        self.failed_rows = failed_rows
        self.errors = errors or []
        self.message = message


class UnifiedImporter:
    """Unified importer for all data types"""
    
    def __init__(self):
        self.google_sheets_importer = GoogleSheetsImporter()
    
    @staticmethod
    def detect_data_type(df: pd.DataFrame) -> str:
        """
        Auto-detect data type based on column headers
        
        Returns: 'sales', 'agents', 'customers', 'products', or 'unknown'
        """
        columns = set(col.lower().strip() for col in df.columns)
        
        # Sales detection
        sales_indicators = {'customer_name', 'product_name', 'quantity', 'price', 'amount', 'date'}
        if len(sales_indicators.intersection(columns)) >= 4:
            return 'sales'
        
        # Agents detection (Google Sheets format)
        agent_indicators = {'region', 'user', 'brand', 'plan', 'sales'}
        agent_indicators_alt = {'регион', 'пользователь', 'торговая марка'}
        if len(agent_indicators.intersection(columns)) >= 3 or len(agent_indicators_alt.intersection(columns)) >= 2:
            return 'agents'
        
        # Customers detection
        customer_indicators = {'name', 'email', 'phone', 'company'}
        if 'email' in columns or 'phone' in columns:
            if 'name' in columns:
                return 'customers'
        
        # Products detection
        product_indicators = {'sku', 'category', 'in_stock'}
        if len(product_indicators.intersection(columns)) >= 2 and 'name' in columns:
            return 'products'
        
        # Fallback: if has name and price, assume products
        if 'name' in columns and 'price' in columns:
            return 'products'
        
        return 'unknown'
    
    async def import_data(
        self,
        df: pd.DataFrame,
        filename: str,
        file_size: int,
        data_type: Optional[str] = None,
        mode: str = "append",
        period_start: Optional[date] = None,
        period_end: Optional[date] = None
    ) -> ImportResult:
        """
        Import data from DataFrame
        
        Args:
            df: DataFrame with data
            filename: Original filename
            file_size: File size in bytes
            data_type: Explicit data type or None for auto-detect
            mode: 'append' or 'replace'
            period_start: For agent data
            period_end: For agent data
        
        Returns:
            ImportResult with import details
        """
        try:
            # ========================================
            # PHASE 1: VALIDATION (BEFORE import_history)
            # ========================================
            
            # Validate file size - max 50MB
            MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
            if file_size > MAX_FILE_SIZE:
                return ImportResult(
                    success=False,
                    data_type='unknown',
                    errors=[f"File too large: {file_size} bytes. Max allowed: {MAX_FILE_SIZE} bytes"],
                    message="File size exceeds maximum limit (50MB)"
                )
            
            # Validate row count - max 50000 rows (increased from 10000)
            MAX_ROWS = 50000
            if len(df) > MAX_ROWS:
                return ImportResult(
                    success=False,
                    data_type='unknown',
                    errors=[f"Too many rows: {len(df)}. Max allowed: {MAX_ROWS}"],
                    message=f"File has too many rows ({len(df)}). Maximum allowed: {MAX_ROWS}"
                )
            
            # Auto-detect data type if not provided
            if not data_type:
                data_type = self.detect_data_type(df)
                logger.info(f"Auto-detected data type: {data_type}")
            
            if data_type == 'unknown':
                return ImportResult(
                    success=False,
                    data_type='unknown',
                    errors=["Could not detect data type from file structure"],
                    message="Unable to determine data type. Please specify explicitly."
                )
            
            # ========================================
            # PHASE 2: CREATE IMPORT_HISTORY (AFTER validation passed)
            # ========================================
            
            # Create import_history record
            import_id = str(uuid4())
            import_record = {
                'id': import_id,
                'filename': filename,
                'file_size': file_size,
                'total_rows': len(df),
                'imported_rows': 0,
                'failed_rows': 0,
                'status': 'processing',
                'progress_percent': 0,
                'import_source': 'unified_upload',
                'import_type': data_type,
                'metadata': {
                    'auto_detected': data_type is None,
                    'mode': mode,
                    'period_start': period_start.isoformat() if period_start else None,
                    'period_end': period_end.isoformat() if period_end else None
                },
                'started_at': datetime.now().isoformat()
            }
            
            supabase.table('import_history').insert(import_record).execute()
            logger.info(f"Created import_history record: {import_id}")
            
            # Import based on data type
            if data_type == 'sales':
                result = await self._import_sales(df, mode, import_id)
            elif data_type == 'agents':
                result = await self._import_agents(df, mode, period_start, period_end, import_id)
            elif data_type == 'customers':
                result = await self._import_customers(df, mode, import_id)
            elif data_type == 'products':
                result = await self._import_products(df, mode, import_id)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
            
            # Update import_history with results
            supabase.table('import_history').update({
                'status': 'completed' if result['success'] else 'failed',
                'imported_rows': result['imported_rows'],
                'failed_rows': result['failed_rows'],
                'progress_percent': 100,
                'completed_at': datetime.now().isoformat(),
                'related_agent_ids': result.get('related_agent_ids', []),
                'related_sale_ids': result.get('related_sale_ids', [])
            }).eq('id', import_id).execute()
            
            return ImportResult(
                success=result['success'],
                import_id=import_id,
                data_type=data_type,
                imported_rows=result['imported_rows'],
                failed_rows=result['failed_rows'],
                errors=result.get('errors', []),
                message=result.get('message', f"Successfully imported {result['imported_rows']} {data_type} records")
            )
        
        except Exception as e:
            logger.error(f"Import error: {e}")
            # Update import_history with error
            if 'import_id' in locals():
                supabase.table('import_history').update({
                    'status': 'failed',
                    'error_log': str(e),
                    'completed_at': datetime.now().isoformat()
                }).eq('id', import_id).execute()
            
            return ImportResult(
                success=False,
                import_id=import_id if 'import_id' in locals() else None,
                data_type=data_type if 'data_type' in locals() else 'unknown',
                errors=[str(e)],
                message=f"Import failed: {str(e)}"
            )
    
    async def _import_sales(
        self, 
        df: pd.DataFrame, 
        mode: str, 
        import_id: str  # Added for progress tracking
    ) -> Dict[str, Any]:
        """Import sales data"""
        try:
            # Replace mode: clear existing sales
            if mode == "replace":
                supabase.table("sale_items").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
                supabase.table("sales").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
            imported = 0
            failed = 0
            sale_ids = []
            errors = []
            
            # Process in batches to prevent memory issues with large files
            # Increased from 100 to 500 for better performance with large files (50K+ rows)
            BATCH_SIZE = 500
            total_rows = len(df)
            
            import time
            import_start_time = time.time()
            logger.info(f"[IMPORT START] Processing {total_rows} rows in batches of {BATCH_SIZE}")
            logger.info(f"[IMPORT CONFIG] Mode: {mode}, Import ID: {import_id}")
            
            for batch_start in range(0, total_rows, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_rows)
                batch_df = df.iloc[batch_start:batch_end]
                batch_start_time = time.time()
                
                logger.info(f"[BATCH {batch_start//BATCH_SIZE + 1}] Processing rows {batch_start}-{batch_end} ({len(batch_df)} rows)")
                
                for idx, row in batch_df.iterrows():
                    try:
                        # Get or create customer
                        customer_name = str(row.get('customer_name', 'Unknown'))
                        customer_result = supabase.table("customers").select("id").eq("name", customer_name).execute()
                        
                        if customer_result.data:
                            customer_id = customer_result.data[0]["id"]
                        else:
                            # Create normalized name (lowercase, stripped)
                            normalized_name = customer_name.lower().strip()
                            new_customer = supabase.table("customers").insert({
                                "name": customer_name,
                                "normalized_name": normalized_name
                            }).execute()
                            customer_id = new_customer.data[0]["id"]
                        
                        # Parse date with GUARANTEED fallback values
                        sale_date = None
                        year = None
                        month = None
                        
                        try:
                            raw_date = row.get('date')
                            if raw_date is not None and raw_date != '':
                                if isinstance(raw_date, str):
                                    # String date
                                    sale_date_obj = pd.to_datetime(raw_date).date()
                                    sale_date = sale_date_obj.isoformat()
                                    year = sale_date_obj.year
                                    month = sale_date_obj.month
                                elif hasattr(raw_date, 'year') and hasattr(raw_date, 'month'):
                                    # Date/datetime object
                                    if hasattr(raw_date, 'date'):
                                        sale_date_obj = raw_date.date()
                                    else:
                                        sale_date_obj = raw_date
                                    sale_date = sale_date_obj.isoformat()
                                    year = sale_date_obj.year
                                    month = sale_date_obj.month
                        except Exception as date_error:
                            logger.warning(f"Date parsing failed: {date_error}, using current date")
                        
                        # GUARANTEED fallback to current date if parsing failed
                        if sale_date is None or year is None or month is None:
                            now = datetime.now()
                            sale_date = now.date().isoformat()
                            year = now.year
                            month = now.month
                        
                        # Get total amount with fallback
                        total = float(row.get('amount', row.get('total', 0)))
                        
                        # Create sale with ALL required fields + import_id for tracking
                        sale = supabase.table("sales").insert({
                            "customer_id": customer_id,
                            "sale_date": sale_date,
                            "year": year,
                            "month": month,
                            "total_amount": total,
                            "import_id": import_id  # ✅ Track which import created this sale
                        }).execute()
                        
                        sale_id = sale.data[0]["id"]
                        sale_ids.append(sale_id)
                        
                        # Add sale items if product info present
                        if 'product_name' in row and row.get('product_name'):
                            product_name = str(row['product_name'])
                            product_result = supabase.table("products").select("id").eq("name", product_name).execute()
                            
                            if product_result.data:
                                product_id = product_result.data[0]["id"]
                            else:
                                # Create normalized name
                                normalized_name = product_name.lower().strip()
                                new_product = supabase.table("products").insert({
                                    "name": product_name,
                                    "normalized_name": normalized_name
                                }).execute()
                                product_id = new_product.data[0]["id"]
                            
                            quantity = int(row.get('quantity', 1))
                            unit_price = float(row.get('price', total / quantity if quantity > 0 else 0))
                            
                            supabase.table("sale_items").insert({
                                "sale_id": sale_id,
                                "product_id": product_id,
                                "quantity": quantity,
                                "unit_price": unit_price,
                                "amount": quantity * unit_price
                            }).execute()
                        
                        imported += 1
                    
                    except Exception as e:
                        error_msg = f"Row {idx}: {str(e)[:100]}"
                        logger.error(f"[ROW ERROR] {error_msg}", exc_info=False)
                        logger.debug(f"Row data: customer={row.get('customer_name')}, date={row.get('date')}, amount={row.get('amount')}")
                        errors.append({
                            'row': int(idx),
                            'customer': str(row.get('customer_name', 'Unknown')),
                            'error': str(e)[:200]
                        })
                        failed += 1
                
                # Explicit cleanup after each batch
                del batch_df
                
                # ✅ Real-time progress update
                batch_time = time.time() - batch_start_time
                progress_percent = min(int((batch_end / total_rows) * 100), 99)  # Cap at 99% until completion
                rows_per_sec = (batch_end - batch_start) / batch_time if batch_time > 0 else 0
                
                try:
                    supabase.table('import_history').update({
                        'progress_percent': progress_percent,
                        'imported_rows': imported,
                        'failed_rows': failed
                    }).eq('id', import_id).execute()
                    logger.info(f"[BATCH COMPLETE] Rows {batch_start}-{batch_end}: {progress_percent}% | "
                               f"Imported: {imported}/{total_rows} | Failed: {failed} | "
                               f"Speed: {rows_per_sec:.1f} rows/sec | Time: {batch_time:.2f}s")
                except Exception as update_error:
                    logger.error(f"[PROGRESS UPDATE FAILED] {update_error}")
                    # Don't fail import if progress update fails
            
            total_time = time.time() - import_start_time
            avg_speed = imported / total_time if total_time > 0 else 0
            logger.info(f"[IMPORT COMPLETE] Total: {imported} imported, {failed} failed in {total_time:.2f}s ({avg_speed:.1f} rows/sec)")
            
            return {
                'success': True,
                'imported_rows': imported,
                'failed_rows': failed,
                'related_sale_ids': sale_ids,
                'errors': errors[:100],  # Limit error list to first 100
                'message': f"Imported {imported} sales records, {failed} failed"
            }
        
        except Exception as e:
            logger.error(f"Sales import error: {e}")
            logger.exception("Full traceback:")
            return {
                'success': False,
                'imported_rows': 0,
                'failed_rows': len(df),
                'errors': [str(e)]
            }
    
    async def _import_agents(
        self,
        df: pd.DataFrame,
        mode: str,
        period_start: Optional[date],
        period_end: Optional[date],
        import_id: str
    ) -> Dict[str, Any]:
        """Import agent data using Google Sheets importer"""
        try:
            # Convert DataFrame to list of lists (Google Sheets format)
            data = [df.columns.tolist()] + df.values.tolist()
            
            # Use existing Google Sheets importer
            result = await self.google_sheets_importer.import_from_data(
                data=data,
                period_start=period_start or date.today(),
                period_end=period_end or date.today(),
                filename=f"Unified Import {import_id}"
            )
            
            return {
                'success': result.success,
                'imported_rows': result.daily_sales_imported,
                'failed_rows': len(result.errors),
                'related_agent_ids': [],  # Will be populated by google_sheets_importer
                'errors': result.errors,
                'message': result.message
            }
        
        except Exception as e:
            logger.error(f"Agent import error: {e}")
            return {
                'success': False,
                'imported_rows': 0,
                'failed_rows': len(df),
                'errors': [str(e)]
            }
    
    async def _import_customers(self, df: pd.DataFrame, mode: str, import_id: str) -> Dict[str, Any]:
        """Import customer data"""
        try:
            if mode == "replace":
                supabase.table("customers").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
            imported = 0
            failed = 0
            
            for _, row in df.iterrows():
                try:
                    customer_name = str(row.get('name', ''))
                    
                    # Check for duplicates in append mode
                    if mode == "append":
                        existing = supabase.table("customers").select("id").eq("name", customer_name).execute()
                        if existing.data:
                            failed += 1
                            continue
                    
                    # Create normalized name
                    normalized_name = customer_name.lower().strip()
                    
                    supabase.table("customers").insert({
                        "name": customer_name,
                        "normalized_name": normalized_name,
                        "email": str(row.get('email', '')) or None,
                        "phone": str(row.get('phone', '')) or None,
                        "company": str(row.get('company', '')) or None
                    }).execute()
                    
                    imported += 1
                
                except Exception as e:
                    logger.error(f"Error importing customer row: {e}")
                    failed += 1
            
            return {
                'success': True,
                'imported_rows': imported,
                'failed_rows': failed,
                'message': f"Imported {imported} customers"
            }
        
        except Exception as e:
            logger.error(f"Customer import error: {e}")
            return {
                'success': False,
                'imported_rows': 0,
                'failed_rows': len(df),
                'errors': [str(e)]
            }
    
    async def _import_products(self, df: pd.DataFrame, mode: str, import_id: str) -> Dict[str, Any]:
        """Import product data"""
        try:
            if mode == "replace":
                supabase.table("products").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            
            imported = 0
            failed = 0
            errors = []
            
            # Safe string helper
            def safe_str(val):
                return str(val) if val is not None and not pd.isna(val) else ''

            # BATCH PROCESSING
            BATCH_SIZE = 500
            total_rows = len(df)

            import time
            import_start_time = time.time()
            logger.info(f"[IMPORT START] Processing {total_rows} rows in batches of {BATCH_SIZE}")

            for batch_start in range(0, total_rows, BATCH_SIZE):
                batch_end = min(batch_start + BATCH_SIZE, total_rows)
                batch_df = df.iloc[batch_start:batch_end]
                batch_start_time = time.time()

                # Pre-fetch existing products to avoid N+1 queries
                existing_skus = set()
                existing_names = set()

                if mode == "append":
                    skus_to_check = set()
                    names_to_check = set()
                    
                    for _, row in batch_df.iterrows():
                        sku = safe_str(row.get('sku', ''))
                        name = safe_str(row.get('name', ''))
                        if sku:
                            skus_to_check.add(sku)
                        elif name:
                            names_to_check.add(name)

                    # Chunked queries to avoid URL length limits
                    CHUNK_SIZE = 100

                    # Check SKUs
                    skus_list = list(skus_to_check)
                    for i in range(0, len(skus_list), CHUNK_SIZE):
                        chunk = skus_list[i:i + CHUNK_SIZE]
                        if chunk:
                            try:
                                res = supabase.table("products").select("sku").in_("sku", chunk).execute()
                                if res.data:
                                    existing_skus.update(item['sku'] for item in res.data)
                            except Exception as e:
                                logger.error(f"Error checking existing SKUs: {e}")

                    # Check Names
                    names_list = list(names_to_check)
                    for i in range(0, len(names_list), CHUNK_SIZE):
                        chunk = names_list[i:i + CHUNK_SIZE]
                        if chunk:
                            try:
                                res = supabase.table("products").select("name").in_("name", chunk).execute()
                                if res.data:
                                    existing_names.update(item['name'] for item in res.data)
                            except Exception as e:
                                logger.error(f"Error checking existing Names: {e}")

                to_insert = []
                # batch_seen_skus/names to handle duplicates within the batch
                batch_seen_skus = set()
                batch_seen_names = set()

                # Prepare insertion list
                for idx, row in batch_df.iterrows():
                    try:
                        product_name = safe_str(row.get('name', ''))
                        sku = safe_str(row.get('sku', ''))
                        
                        # Logic to skip
                        skip = False

                        if mode == "append":
                            if sku:
                                if sku in existing_skus or sku in batch_seen_skus:
                                    skip = True
                            else:
                                if product_name in existing_names or product_name in batch_seen_names:
                                    skip = True
                        else:
                            # Replace mode: duplicates within file check
                            if sku and sku in batch_seen_skus:
                                skip = True
                            elif not sku and product_name in batch_seen_names:
                                skip = True

                        if skip:
                            failed += 1
                            continue

                        if sku:
                            batch_seen_skus.add(sku)
                        else:
                            batch_seen_names.add(product_name)

                        item = {
                            "name": product_name,
                            "sku": sku or None,
                            "price": float(row.get('price', 0)),
                            "category": safe_str(row.get('category', '')) or None,
                            "in_stock": int(row.get('in_stock', 0)) if row.get('in_stock') else 0
                        }
                        to_insert.append(item)

                    except Exception as e:
                        logger.error(f"Error preparing product row: {e}")
                        failed += 1
                        errors.append(str(e))

                # Bulk insert
                if to_insert:
                    try:
                        supabase.table("products").insert(to_insert).execute()
                        imported += len(to_insert)
                    except Exception as e:
                        logger.error(f"Bulk insert failed: {e}. Falling back to individual insert.")
                        # Fallback to individual
                        for item in to_insert:
                            try:
                                supabase.table("products").insert(item).execute()
                                imported += 1
                            except Exception as inner_e:
                                failed += 1
                                logger.error(f"Individual insert error: {inner_e}")
                                errors.append(str(inner_e))

                # Explicit cleanup
                del batch_df
                
                # Progress update
                batch_time = time.time() - batch_start_time
                progress_percent = min(int((batch_end / total_rows) * 100), 99)
                rows_per_sec = (batch_end - batch_start) / batch_time if batch_time > 0 else 0

                try:
                    supabase.table('import_history').update({
                        'progress_percent': progress_percent,
                        'imported_rows': imported,
                        'failed_rows': failed
                    }).eq('id', import_id).execute()
                    logger.info(f"[BATCH COMPLETE] Rows {batch_start}-{batch_end}: {progress_percent}% | "
                               f"Imported: {imported}/{total_rows} | Failed: {failed} | "
                               f"Speed: {rows_per_sec:.1f} rows/sec")
                except Exception as update_error:
                    logger.error(f"[PROGRESS UPDATE FAILED] {update_error}")

            total_time = time.time() - import_start_time
            avg_speed = imported / total_time if total_time > 0 else 0
            logger.info(f"[IMPORT COMPLETE] Total: {imported} imported, {failed} failed in {total_time:.2f}s")

            return {
                'success': True,
                'imported_rows': imported,
                'failed_rows': failed,
                'message': f"Imported {imported} products",
                'errors': errors[:100]
            }
        
        except Exception as e:
            logger.error(f"Product import error: {e}")
            return {
                'success': False,
                'imported_rows': 0,
                'failed_rows': len(df),
                'errors': [str(e)]
            }
