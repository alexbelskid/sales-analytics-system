"""
Excel Parser Service
Memory-efficient parser for large Excel files (64MB+)
Uses openpyxl in read_only mode with chunked processing
"""

from openpyxl import load_workbook
from datetime import datetime, date
from typing import Generator, Dict, Any, List, Optional, Tuple
import re
import logging

logger = logging.getLogger(__name__)


class ExcelParser:
    """Memory-efficient Excel parser for large files"""
    
    # Column mapping based on Excel structure analysis
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
    
    def count_rows(self) -> int:
        """Count total rows in Excel file"""
        try:
            wb = load_workbook(self.file_path, read_only=True, data_only=True)
            ws = wb.active
            self.total_rows = ws.max_row - 1  # Exclude header
            wb.close()
            return self.total_rows
        except Exception as e:
            logger.error(f"Error counting rows: {e}")
            return 0
    
    def parse_chunks(self) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Parse Excel file in chunks to save memory
        Yields batches of parsed rows
        """
        try:
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
                    if len(self.errors) < 100:  # Limit error log
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
            logger.error(f"Excel parsing error: {e}")
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
        
        # Already a date/datetime
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        
        # String parsing
        if isinstance(value, str):
            value = value.strip()
            
            # Try DD.MM.YYYY
            for fmt in ['%d.%m.%Y', '%d.%m.%y', '%Y-%m-%d', '%d/%m/%Y']:
                try:
                    return datetime.strptime(value, fmt).date()
                except:
                    continue
        
        return None
    
    def _parse_number(self, value: Any) -> Optional[float]:
        """Parse number from string or number"""
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
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
