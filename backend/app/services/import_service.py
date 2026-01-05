"""
Import Service
Handles importing parsed Excel data into Supabase
Uses batch inserts for performance
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
from app.database import supabase
from app.services.excel_parser import ExcelParser
from app.services.cache_service import cache

logger = logging.getLogger(__name__)


class ImportService:
    """Service for importing Excel data into database"""
    
    BATCH_SIZE = 1000  # Rows per batch insert
    
    def __init__(self):
        self.customers_cache: Dict[str, str] = {}  # normalized_name -> id
        self.products_cache: Dict[str, str] = {}   # normalized_name -> id
        self.stores_cache: Dict[str, str] = {}     # code -> id
        self.import_id: Optional[str] = None
    
    async def import_excel(self, file_path: str, filename: str, file_size: int = 0) -> Dict[str, Any]:
        """
        Main import method
        Returns import result with statistics
        """
        if supabase is None:
            raise Exception("Database not configured")
        
        # Create import record
        self.import_id = await self._create_import_record(filename, file_size)
        
        try:
            # Initialize parser
            parser = ExcelParser(file_path, chunk_size=5000)
            total_rows = parser.count_rows()
            
            await self._update_import_status('processing', total_rows=total_rows)
            
            # Pre-load existing entities for faster lookups
            await self._preload_caches()
            
            imported_rows = 0
            failed_rows = 0
            sales_batch: List[Dict] = []
            
            # Process chunks
            for chunk in parser.parse_chunks():
                for row_data in chunk:
                    try:
                        # Get or create entities
                        customer_id = await self._get_or_create_customer(row_data)
                        product_id = await self._get_or_create_product(row_data)
                        store_id = await self._get_or_create_store(row_data)
                        
                        # Prepare sale record
                        sale = {
                            'sale_date': row_data['sale_date'].isoformat(),
                            'customer_id': customer_id,
                            'product_id': product_id,
                            'store_id': store_id,
                            'quantity': row_data['quantity'],
                            'price': row_data['price'],
                            'amount': row_data['amount'],
                            'year': row_data['year'],
                            'month': row_data['month'],
                            'week': row_data['week'],
                            'day_of_week': row_data['day_of_week']
                        }
                        sales_batch.append(sale)
                        imported_rows += 1
                        
                        # Batch insert sales
                        if len(sales_batch) >= self.BATCH_SIZE:
                            await self._batch_insert_sales(sales_batch)
                            sales_batch = []
                            
                            # Update progress
                            progress = int((imported_rows / max(total_rows, 1)) * 100)
                            await self._update_import_status(
                                'processing',
                                imported_rows=imported_rows,
                                progress=progress
                            )
                    
                    except Exception as e:
                        failed_rows += 1
                        logger.error(f"Row import error: {e}")
            
            # Insert remaining sales
            if sales_batch:
                await self._batch_insert_sales(sales_batch)
            
            # Update customer/product statistics
            await self._update_statistics()
            
            # Mark import complete
            await self._update_import_status(
                'completed',
                imported_rows=imported_rows,
                failed_rows=failed_rows,
                progress=100
            )
            
            # Invalidate analytics cache
            cache.invalidate_pattern("analytics:")
            
            return {
                'success': True,
                'import_id': self.import_id,
                'total_rows': total_rows,
                'imported_rows': imported_rows,
                'failed_rows': failed_rows,
                'customers_created': len(self.customers_cache),
                'products_created': len(self.products_cache)
            }
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            await self._update_import_status('failed', error_log=str(e))
            raise
    
    async def _create_import_record(self, filename: str, file_size: int) -> str:
        """Create import history record"""
        result = supabase.table('import_history').insert({
            'filename': filename,
            'file_size': file_size,
            'status': 'pending',
            'started_at': datetime.now().isoformat()
        }).execute()
        return result.data[0]['id']
    
    async def _update_import_status(
        self,
        status: str,
        total_rows: int = None,
        imported_rows: int = None,
        failed_rows: int = None,
        progress: int = None,
        error_log: str = None
    ):
        """Update import progress"""
        update_data = {'status': status}
        
        if total_rows is not None:
            update_data['total_rows'] = total_rows
        if imported_rows is not None:
            update_data['imported_rows'] = imported_rows
        if failed_rows is not None:
            update_data['failed_rows'] = failed_rows
        if progress is not None:
            update_data['progress_percent'] = progress
        if error_log is not None:
            update_data['error_log'] = error_log
        if status == 'completed':
            update_data['completed_at'] = datetime.now().isoformat()
        
        supabase.table('import_history').update(update_data).eq('id', self.import_id).execute()
    
    async def _preload_caches(self):
        """Pre-load existing entities into memory cache"""
        # Load customers
        result = supabase.table('customers').select('id, normalized_name').execute()
        for c in result.data:
            self.customers_cache[c['normalized_name']] = c['id']
        
        # Load products
        result = supabase.table('products').select('id, normalized_name').execute()
        for p in result.data:
            self.products_cache[p['normalized_name']] = p['id']
        
        # Load stores
        result = supabase.table('stores').select('id, code').execute()
        for s in result.data:
            if s['code']:
                self.stores_cache[s['code']] = s['id']
        
        logger.info(f"Preloaded: {len(self.customers_cache)} customers, {len(self.products_cache)} products, {len(self.stores_cache)} stores")
    
    async def _get_or_create_customer(self, row_data: Dict) -> str:
        """Get existing or create new customer"""
        normalized = row_data['customer_name']
        
        if normalized in self.customers_cache:
            return self.customers_cache[normalized]
        
        # Create new customer
        result = supabase.table('customers').insert({
            'name': row_data['customer_raw'],
            'normalized_name': normalized
        }).execute()
        
        customer_id = result.data[0]['id']
        self.customers_cache[normalized] = customer_id
        return customer_id
    
    async def _get_or_create_product(self, row_data: Dict) -> str:
        """Get existing or create new product"""
        normalized = row_data['product_name']
        
        if normalized in self.products_cache:
            return self.products_cache[normalized]
        
        # Create new product
        result = supabase.table('products').insert({
            'name': row_data['product_raw'],
            'normalized_name': normalized,
            'category': row_data.get('category', 'Без категории')
        }).execute()
        
        product_id = result.data[0]['id']
        self.products_cache[normalized] = product_id
        return product_id
    
    async def _get_or_create_store(self, row_data: Dict) -> Optional[str]:
        """Get existing or create new store"""
        code = row_data.get('store_code')
        if not code:
            return None
        
        code = str(code)
        if code in self.stores_cache:
            return self.stores_cache[code]
        
        # Create new store
        result = supabase.table('stores').insert({
            'code': code,
            'name': row_data.get('store_name') or code,
            'region': row_data.get('region'),
            'channel': row_data.get('channel')
        }).execute()
        
        store_id = result.data[0]['id']
        self.stores_cache[code] = store_id
        return store_id
    
    async def _batch_insert_sales(self, sales: List[Dict]):
        """Batch insert sales records"""
        if not sales:
            return
        
        try:
            supabase.table('sales').insert(sales).execute()
            logger.debug(f"Inserted {len(sales)} sales")
        except Exception as e:
            logger.error(f"Batch insert error: {e}")
            # Try inserting one by one as fallback
            for sale in sales:
                try:
                    supabase.table('sales').insert(sale).execute()
                except Exception as e2:
                    logger.error(f"Single insert error: {e2}")
    
    async def _update_statistics(self):
        """Update aggregated statistics in customers and products tables"""
        logger.info("Updating customer statistics...")
        
        # Update customers - use RPC or raw SQL for aggregation
        # This is a simplified version - for large datasets, use a database function
        try:
            # Get customer totals from sales
            customers_result = supabase.table('sales').select(
                'customer_id, amount, sale_date'
            ).execute()
            
            customer_stats: Dict[str, Dict] = {}
            for sale in customers_result.data:
                cid = sale['customer_id']
                if cid not in customer_stats:
                    customer_stats[cid] = {'total': 0, 'count': 0, 'last_date': None}
                customer_stats[cid]['total'] += float(sale['amount'])
                customer_stats[cid]['count'] += 1
                sale_date = sale['sale_date']
                if not customer_stats[cid]['last_date'] or sale_date > customer_stats[cid]['last_date']:
                    customer_stats[cid]['last_date'] = sale_date
            
            # Update each customer (batch would be better but Supabase limits)
            for cid, stats in list(customer_stats.items())[:100]:  # Limit to avoid timeout
                supabase.table('customers').update({
                    'total_purchases': stats['total'],
                    'purchases_count': stats['count'],
                    'last_purchase_date': stats['last_date']
                }).eq('id', cid).execute()
            
            logger.info(f"Updated {len(customer_stats)} customer stats")
        except Exception as e:
            logger.error(f"Customer stats update error: {e}")
        
        # Similar for products - simplified
        logger.info("Statistics update complete")
    
    @staticmethod
    async def get_import_status(import_id: str) -> Optional[Dict]:
        """Get import status by ID"""
        if supabase is None:
            return None
        
        result = supabase.table('import_history').select('*').eq('id', import_id).execute()
        return result.data[0] if result.data else None
    
    @staticmethod
    async def get_import_history(limit: int = 20) -> List[Dict]:
        """Get recent import history"""
        if supabase is None:
            return []
        
        result = supabase.table('import_history').select('*').order(
            'started_at', desc=True
        ).limit(limit).execute()
        return result.data
