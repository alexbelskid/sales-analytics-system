"""
Excel Parser Service
Memory-efficient parser for large Excel files (64MB+)
Supports both .xlsx (openpyxl) and .xls (xlrd via pandas) formats
"""

from datetime import datetime, date
from typing import Generator, Dict, Any, List, Optional
import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)


class ExcelParser:
    """Memory-efficient Excel parser for large files"""
    
    # Column mapping based on Excel structure analysis
    # You may need to adjust these based on your actual Excel columns
    COLUMN_MAP = {
        'date': 1,           # B: Дата (формат: ДД.ММ.ГГГГ)
        'store_code': 3,     # D: Код точки (Y001T4)
        'region': 4,         # E: Регион
        'channel': 5,        # F: Канал сбыта
        'store_name': 6,     # G: Город/Точка
        'customer': 8,       # I: Контрагент (юр.лицо)
        'address': 9,        # J: Адрес
        'category': 11,      # L: Группа товара
        'product_type': 12,  # M: Вид товара
        'product': 13,       # N: Номенклатура (название товара)
        'barcode': 14,       # O: Штрихкод
        'quantity': 16,      # Q: Количество
        'amount': 17,        # R: Сумма с НДС
    }
    
    def __init__(self, file_path: str, chunk_size: int = 5000):
        self.file_path = file_path
        self.chunk_size = chunk_size
        self.total_rows = 0
        self.processed_rows = 0
        self.failed_rows = 0
        self.errors: List[str] = []
        self._use_pandas = False
    
    def count_rows(self) -> int:
        """Count total rows in Excel file"""
        try:
            # Try openpyxl first
            from openpyxl import load_workbook
            wb = load_workbook(self.file_path, read_only=True, data_only=True)
            ws = wb.active
            self.total_rows = ws.max_row - 1  # Exclude header
            wb.close()
            self._use_pandas = False
            return self.total_rows
        except Exception as e:
            logger.warning(f"openpyxl failed, trying pandas: {e}")
            # Fallback to pandas
            try:
                # Read just first few rows to estimate
                df_sample = pd.read_excel(self.file_path, nrows=0)
                # Read full file in chunks to count
                total = 0
                for chunk in pd.read_excel(self.file_path, chunksize=10000):
                    total += len(chunk)
                self.total_rows = total
                self._use_pandas = True
                return self.total_rows
            except Exception as e2:
                logger.error(f"Error counting rows: {e2}")
                return 0
    
    def parse_chunks(self) -> Generator[List[Dict[str, Any]], None, None]:
        """Parse Excel file in chunks to save memory"""
        
        if self._use_pandas or self._should_use_pandas():
            yield from self._parse_with_pandas()
        else:
            yield from self._parse_with_openpyxl()
    
    def _should_use_pandas(self) -> bool:
        """Check if we should use pandas instead of openpyxl"""
        try:
            from openpyxl import load_workbook
            wb = load_workbook(self.file_path, read_only=True, data_only=True)
            wb.close()
            return False
        except Exception as e:
            logger.warning(f"openpyxl not compatible, using pandas: {e}")
            return True
    
    def _parse_with_pandas(self) -> Generator[List[Dict[str, Any]], None, None]:
        """Parse using pandas for maximum compatibility"""
        logger.info("Using pandas parser for Excel file")
        
        try:
            # Read entire file (pandas doesn't support chunksize for Excel)
            logger.info("Reading Excel file with pandas...")
            df = pd.read_excel(self.file_path, header=0)
            self.total_rows = len(df)
            logger.info(f"Loaded {self.total_rows} rows")
            
            # Process in chunks manually
            chunk_num = 0
            parsed_chunk: List[Dict[str, Any]] = []
            
            for idx, row in df.iterrows():
                try:
                    parsed = self._parse_pandas_row(row, idx + 2)  # +2 for 1-indexed + header
                    if parsed:
                        parsed_chunk.append(parsed)
                        self.processed_rows += 1
                    else:
                        self.failed_rows += 1
                except Exception as e:
                    self.failed_rows += 1
                    if len(self.errors) < 100:
                        self.errors.append(f"Row {idx + 2}: {str(e)}")
                
                # Yield chunk when full
                if len(parsed_chunk) >= self.chunk_size:
                    chunk_num += 1
                    logger.info(f"Chunk {chunk_num}: {self.processed_rows} success, {self.failed_rows} failed")
                    yield parsed_chunk
                    parsed_chunk = []
                
                # Log progress
                if (idx + 1) % 10000 == 0:
                    logger.info(f"Progress: {idx + 1}/{self.total_rows} rows")
            
            # Yield remaining
            if parsed_chunk:
                yield parsed_chunk
            
            logger.info(f"Pandas parsing complete: {self.processed_rows} success, {self.failed_rows} failed")
            
        except Exception as e:
            logger.error(f"Pandas Excel parsing error: {e}")
            raise
    
    def _parse_pandas_row(self, row: pd.Series, row_num: int) -> Optional[Dict[str, Any]]:
        """Parse a pandas row into structured data"""
        
        # Get values by column index
        cols = row.values
        
        date_val = self._safe_get(cols, self.COLUMN_MAP['date'])
        customer = self._safe_get(cols, self.COLUMN_MAP['customer'])
        product = self._safe_get(cols, self.COLUMN_MAP['product'])
        quantity = self._safe_get(cols, self.COLUMN_MAP['quantity'])
        amount = self._safe_get(cols, self.COLUMN_MAP['amount'])
        
        # Validate required fields
        if pd.isna(customer) or pd.isna(product):
            return None
        
        customer = str(customer)
        product = str(product)
        
        if not customer.strip() or not product.strip():
            return None
        
        # Parse date
        sale_date = self._parse_date(date_val)
        if not sale_date:
            return None
        
        # Parse numbers
        qty = self._parse_number(quantity)
        amt = self._parse_number(amount)
        
        if amt is None or amt <= 0:
            return None
        
        # Calculate price per unit
        price = amt / qty if qty and qty > 0 else amt
        
        return {
            'row_num': row_num,
            'sale_date': sale_date,
            'customer_name': self._normalize_name(customer),
            'customer_raw': customer,
            'product_name': self._normalize_name(product),
            'product_raw': product,
            'category': str(self._safe_get(cols, self.COLUMN_MAP['category']) or 'Без категории'),
            'store_code': self._safe_get(cols, self.COLUMN_MAP['store_code']),
            'store_name': self._safe_get(cols, self.COLUMN_MAP['store_name']),
            'region': self._safe_get(cols, self.COLUMN_MAP['region']),
            'channel': self._safe_get(cols, self.COLUMN_MAP['channel']),
            'quantity': qty or 1,
            'price': round(price, 2),
            'amount': round(amt, 2),
            'year': sale_date.year,
            'month': sale_date.month,
            'week': sale_date.isocalendar()[1],
            'day_of_week': sale_date.weekday()
        }
    
    def _safe_get(self, arr, idx: int) -> Any:
        """Safely get value from array"""
        try:
            if idx < len(arr):
                val = arr[idx]
                if pd.isna(val):
                    return None
                return val
            return None
        except:
            return None
    
    def _parse_with_openpyxl(self) -> Generator[List[Dict[str, Any]], None, None]:
        """Parse using openpyxl (original method)"""
        logger.info("Using openpyxl parser for Excel file")
        
        try:
            from openpyxl import load_workbook
            wb = load_workbook(self.file_path, read_only=True, data_only=True)
            ws = wb.active
            
            chunk: List[Dict[str, Any]] = []
            row_num = 0
            
            for row in ws.iter_rows(min_row=2, values_only=True):  # Skip header
                row_num += 1
                
                try:
                    parsed = self._parse_row(row, row_num)
                    if parsed:
                        chunk.append(parsed)
                        self.processed_rows += 1
                    else:
                        self.failed_rows += 1
                except Exception as e:
                    self.failed_rows += 1
                    if len(self.errors) < 100:
                        self.errors.append(f"Row {row_num}: {str(e)}")
                
                # Yield chunk when full
                if len(chunk) >= self.chunk_size:
                    logger.info(f"Parsed {row_num} rows...")
                    yield chunk
                    chunk = []
                
                # Log progress every 10,000 rows
                if row_num % 10000 == 0:
                    logger.info(f"Progress: {row_num} rows processed, {self.failed_rows} failed")
            
            # Yield remaining rows
            if chunk:
                yield chunk
            
            wb.close()
            logger.info(f"Parsing complete: {self.processed_rows} success, {self.failed_rows} failed")
            
        except Exception as e:
            logger.error(f"openpyxl parsing error: {e}")
            raise
    
    def _parse_row(self, row: tuple, row_num: int) -> Optional[Dict[str, Any]]:
        """Parse a single row into structured data"""
        
        # Get values using column map
        date_val = self._get_cell(row, self.COLUMN_MAP['date'])
        customer = self._get_cell(row, self.COLUMN_MAP['customer'])
        product = self._get_cell(row, self.COLUMN_MAP['product'])
        quantity = self._get_cell(row, self.COLUMN_MAP['quantity'])
        amount = self._get_cell(row, self.COLUMN_MAP['amount'])
        
        # Validate required fields
        if not customer or not product:
            return None
        
        # Parse date
        sale_date = self._parse_date(date_val)
        if not sale_date:
            return None
        
        # Parse numbers
        qty = self._parse_number(quantity)
        amt = self._parse_number(amount)
        
        if amt is None or amt <= 0:
            return None
        
        # Calculate price per unit
        price = amt / qty if qty and qty > 0 else amt
        
        return {
            'row_num': row_num,
            'sale_date': sale_date,
            'customer_name': self._normalize_name(str(customer)),
            'customer_raw': str(customer),
            'product_name': self._normalize_name(str(product)),
            'product_raw': str(product),
            'category': self._get_cell(row, self.COLUMN_MAP['category']) or 'Без категории',
            'store_code': self._get_cell(row, self.COLUMN_MAP['store_code']),
            'store_name': self._get_cell(row, self.COLUMN_MAP['store_name']),
            'region': self._get_cell(row, self.COLUMN_MAP['region']),
            'channel': self._get_cell(row, self.COLUMN_MAP['channel']),
            'quantity': qty or 1,
            'price': round(price, 2),
            'amount': round(amt, 2),
            'year': sale_date.year,
            'month': sale_date.month,
            'week': sale_date.isocalendar()[1],
            'day_of_week': sale_date.weekday()
        }
    
    def _get_cell(self, row: tuple, col_index: int) -> Any:
        """Safely get cell value by index"""
        try:
            if col_index < len(row):
                val = row[col_index]
                return val if val is not None else None
            return None
        except:
            return None
    
    def _parse_date(self, value: Any) -> Optional[date]:
        """Parse date from various formats"""
        if value is None:
            return None
        
        # Handle pandas Timestamp
        if hasattr(value, 'date'):
            try:
                return value.date()
            except:
                pass
        
        # Already a date/datetime
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        
        # String parsing
        if isinstance(value, str):
            value = value.strip()
            
            # Try various formats
            for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d']:
                try:
                    return datetime.strptime(value, fmt).date()
                except:
                    continue
        
        # Try parsing as number (Excel serial date)
        if isinstance(value, (int, float)):
            try:
                # Excel date starts from 1899-12-30
                from datetime import timedelta
                return (datetime(1899, 12, 30) + timedelta(days=int(value))).date()
            except:
                pass
        
        return None
    
    def _parse_number(self, value: Any) -> Optional[float]:
        """Parse number from string or number"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            if pd.isna(value):
                return None
            return float(value)
        
        if isinstance(value, str):
            # Remove spaces, replace comma with dot
            value = value.strip().replace(' ', '').replace(',', '.')
            try:
                return float(value)
            except:
                return None
        
        return None
    
    def _normalize_name(self, name: str) -> str:
        """Normalize company/product name for deduplication"""
        if not name:
            return ''
        
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove common prefixes/suffixes
        remove_patterns = [
            r'^ооо\s+',
            r'^оао\s+',
            r'^зао\s+',
            r'^ип\s+',
            r'^чуп\s+',
            r'^уп\s+',
            r'\s+ооо$',
            r'\s+оао$',
            r'"',
            r"'",
        ]
        
        for pattern in remove_patterns:
            normalized = re.sub(pattern, '', normalized)
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def get_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return {
            'total_rows': self.total_rows,
            'processed_rows': self.processed_rows,
            'failed_rows': self.failed_rows,
            'success_rate': round(self.processed_rows / max(self.total_rows, 1) * 100, 1),
            'errors': self.errors[:20]  # First 20 errors
        }
