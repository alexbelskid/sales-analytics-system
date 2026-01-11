"""
Google Sheets Importer Service
Imports agent sales data from Google Sheets (Daily Sales-Out format)
"""

from typing import List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import logging
import re

from app.database import supabase
from app.models.agent_analytics import GoogleSheetsImportResult

logger = logging.getLogger(__name__)


class GoogleSheetsImporter:
    """Service for importing agent data from Google Sheets"""
    
    # Regional headers - настоящие регионы Беларуси (не компании!)
    REGIONAL_HEADERS = [
        'БРЕСТ', 
        'ВИТЕБСК', 
        'ГОМЕЛЬ', 
        'ГРОДНО', 
        'МИНСК',
        'МОГИЛЕВ'
    ]
    
    # Компании/клиенты, которые НЕ являются регионами
    NON_REGION_KEYWORDS = ['КАМ РЕКИТТ', 'ЮМСА', 'РЕКИТТ', 'ЮМС']
    
    def __init__(self):
        self.supabase = supabase
    
    async def import_from_data(
        self,
        data: List[List[Any]],
        period_start: date,
        period_end: date
    ) -> GoogleSheetsImportResult:
        """
        Import agent data from parsed Google Sheets data
        
        Expected format (from "Daily Sales-Out"):
        Row with region header (e.g., "БРЕСТ")
        Then rows with: Agent Name | Sales | Plan | Fulfillment % | Forecast % | ... (categories) | 1 | 2 | 3 | ...
        """
        try:
            agents_imported = 0
            plans_imported = 0
            daily_sales_imported = 0
            errors = []
            processed_names = set()
            
            current_region = None
            header_row_idx = None
            
            logger.info(f"Starting import of {len(data)} rows")
            
            for row_idx, row in enumerate(data):
                if not row or len(row) == 0:
                    continue
                
                # Get first cell
                first_cell = str(row[0]).strip() if row[0] else ""
                first_cell_upper = first_cell.upper()
                
                # Skip completely empty or very short cells
                if len(first_cell) < 2:
                    continue
                
                # Проверяем что это НЕ компания/клиент
                is_non_region = any(keyword in first_cell_upper for keyword in self.NON_REGION_KEYWORDS)
                if is_non_region:
                    logger.debug(f"Row {row_idx}: Skipping non-region company: {first_cell}")
                    continue
                
                # Check if this is a regional header
                # Региональная строка - это строка, которая содержит ТОЛЬКО название региона
                # и не содержит числовых данных в колонках B-H (продажи, план и т.д.)
                is_region_header = False
                if any(reg in first_cell_upper for reg in self.REGIONAL_HEADERS):
                    # Проверяем что в колонках B-H нет данных (это признак региональной строки)
                    has_sales_data = any(
                        self._parse_float(row[i]) is not None 
                        for i in range(1, min(8, len(row)))
                    )
                    if not has_sales_data:
                        is_region_header = True
                        # Сохраняем полное название региона
                        current_region = first_cell
                        logger.info(f"Row {row_idx}: Found region header: {current_region}")
                        continue
                
                # Skip column header rows (contain column titles like "Район / Ответственный", "Продажи", etc.)
                skip_keywords = ['РАЙОН', 'ОТВЕТСТВЕННЫЙ', 'ПРОДАЖИ', 'ПЛАН', 'ВЫПОЛНЕНИЕ', 
                                'ПРОГНОЗ', 'БЕЛПОЧТА', 'ПОТРЕБКООП', 'ПИРОТЕХНИКА',
                                'РЕГИОН', 'ПОЛЬЗОВАТЕЛЬ', 'ТОРГОВАЯ МАРКА']
                if any(kw in first_cell_upper for kw in skip_keywords):
                    header_row_idx = row_idx
                    logger.info(f"Row {row_idx}: Skipping header row")
                    continue
                
                # Skip summary/total rows
                if any(word in first_cell_upper for word in ['ИТОГО', 'TOTAL', 'ВСЕГО', 'ОБЩИЙ']):
                    logger.info(f"Row {row_idx}: Skipping summary row: {first_cell}")
                    continue
                
                # Skip if first cell is a number (likely data cell, not agent name)
                if self._parse_float(first_cell) is not None and first_cell.replace('.', '').replace(',', '').isdigit():
                    continue
                
                # This should be an agent row - agent name should be a text string with letters
                # Check if it looks like a name (contains Cyrillic or Latin letters)
                has_letters = any(c.isalpha() for c in first_cell)
                if not has_letters:
                    continue
                
                agent_name = first_cell
                
                # Skip duplicate names in same import
                if agent_name in processed_names:
                    continue
                processed_names.add(agent_name)
                
                # Try to parse agent row
                try:
                    # Parse sales data - columns B, C, D, E
                    sales = self._parse_float(row[1] if len(row) > 1 else None)
                    plan = self._parse_float(row[2] if len(row) > 2 else None)
                    fulfillment_pct = self._parse_float(row[3] if len(row) > 3 else None)
                    forecast_pct = self._parse_float(row[4] if len(row) > 4 else None)
                    
                    # Skip if no sales data at all
                    if sales is None and plan is None:
                        logger.debug(f"Row {row_idx}: Skipping {agent_name} - no sales/plan data")
                        continue
                    
                    # Parse special categories (БелПочта, Потребкооперация, ПИРОТЕХНИКА) - columns F, G, H
                    belpochta = self._parse_float(row[5] if len(row) > 5 else None) or 0
                    potrebkoop = self._parse_float(row[6] if len(row) > 6 else None) or 0
                    pyrotech = self._parse_float(row[7] if len(row) > 7 else None) or 0
                    
                    logger.info(f"Row {row_idx}: Importing agent '{agent_name}' - region: {current_region}, sales: {sales}, plan: {plan}")
                    
                    # Create or update agent
                    agent_id = await self._upsert_agent(agent_name, current_region or 'Unknown')
                    if agent_id:
                        agents_imported += 1
                        
                        # Create sales plan
                        if plan and plan > 0:
                            await self._upsert_sales_plan(
                                agent_id, period_start, period_end, plan, current_region
                            )
                            plans_imported += 1
                        
                        # Create daily sales entry (current sales as of today)
                        if sales and sales > 0:
                            today = date.today()
                            await self._upsert_daily_sales(
                                agent_id, today, sales, current_region, 'General'
                            )
                            daily_sales_imported += 1
                        
                        # Create category sales
                        if belpochta > 0:
                            await self._upsert_daily_sales(
                                agent_id, date.today(), belpochta, current_region, 'БелПочта'
                            )
                            daily_sales_imported += 1
                        
                        if potrebkoop > 0:
                            await self._upsert_daily_sales(
                                agent_id, date.today(), potrebkoop, current_region, 'Потребкооперация'
                            )
                            daily_sales_imported += 1
                        
                        if pyrotech > 0:
                            await self._upsert_daily_sales(
                                agent_id, date.today(), pyrotech, current_region, 'ПИРОТЕХНИКА'
                            )
                            daily_sales_imported += 1
                
                except Exception as row_error:
                    error_msg = f"Error processing row {row_idx} ({agent_name}): {str(row_error)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            logger.info(f"Import complete: {agents_imported} agents, {plans_imported} plans, {daily_sales_imported} sales")
            
            return GoogleSheetsImportResult(
                success=True,
                agents_imported=agents_imported,
                plans_imported=plans_imported,
                daily_sales_imported=daily_sales_imported,
                errors=errors,
                message=f"Успешно импортировано: {agents_imported} агентов, {plans_imported} планов, {daily_sales_imported} записей продаж"
            )
        
        except Exception as e:
            logger.error(f"Import error: {e}")
            return GoogleSheetsImportResult(
                success=False,
                errors=[str(e)],
                message=f"Ошибка импорта: {str(e)}"
            )
    
    # ========================================================================
    # Helper Methods
    # ========================================================================
    
    def _parse_float(self, value: Any) -> float | None:
        """Parse float value from cell, handling various formats"""
        if value is None or value == '':
            return None
        
        try:
            # Remove spaces and convert commas to dots
            s = str(value).strip().replace(' ', '').replace(',', '.')
            
            # Remove any non-numeric characters except dot and minus
            s = re.sub(r'[^\d.-]', '', s)
            
            if not s or s == '-':
                return None
            
            return float(s)
        except:
            return None
    
    async def _upsert_agent(self, name: str, region: str) -> str | None:
        """Create or update agent, returns agent_id"""
        try:
            # Check if agent exists
            result = self.supabase.table("agents").select("id").eq("name", name).execute()
            
            if result.data and len(result.data) > 0:
                # Update existing agent
                agent_id = result.data[0]['id']
                self.supabase.table("agents").update({
                    "region": region
                }).eq("id", agent_id).execute()
                return agent_id
            else:
                # Create new agent
                new_agent = self.supabase.table("agents").insert({
                    "name": name,
                    "email": f"{name.lower().replace(' ', '.')}@company.com",  # Placeholder
                    "region": region,
                    "is_active": True
                }).execute()
                
                if new_agent.data and len(new_agent.data) > 0:
                    return new_agent.data[0]['id']
                return None
        
        except Exception as e:
            logger.error(f"Error upserting agent {name}: {e}")
            return None
    
    async def _upsert_sales_plan(
        self,
        agent_id: str,
        period_start: date,
        period_end: date,
        plan_amount: float,
        region: str
    ):
        """Create or update sales plan"""
        try:
            # Check if plan exists
            result = self.supabase.table("agent_sales_plans").select("id").eq(
                "agent_id", agent_id
            ).eq("period_start", period_start.isoformat()).eq(
                "period_end", period_end.isoformat()
            ).execute()
            
            if result.data and len(result.data) > 0:
                # Update existing plan
                self.supabase.table("agent_sales_plans").update({
                    "plan_amount": plan_amount,
                    "region": region
                }).eq("id", result.data[0]['id']).execute()
            else:
                # Create new plan
                self.supabase.table("agent_sales_plans").insert({
                    "agent_id": agent_id,
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "plan_amount": plan_amount,
                    "region": region
                }).execute()
        
        except Exception as e:
            logger.error(f"Error upserting sales plan: {e}")
    
    async def _upsert_daily_sales(
        self,
        agent_id: str,
        sale_date: date,
        amount: float,
        region: str,
        category: str
    ):
        """Create or update daily sales record"""
        try:
            # Check if record exists
            result = self.supabase.table("agent_daily_sales").select("id").eq(
                "agent_id", agent_id
            ).eq("sale_date", sale_date.isoformat()).eq(
                "category", category
            ).execute()
            
            if result.data and len(result.data) > 0:
                # Update existing record
                self.supabase.table("agent_daily_sales").update({
                    "amount": amount,
                    "region": region
                }).eq("id", result.data[0]['id']).execute()
            else:
                # Create new record
                self.supabase.table("agent_daily_sales").insert({
                    "agent_id": agent_id,
                    "sale_date": sale_date.isoformat(),
                    "amount": amount,
                    "region": region,
                    "category": category
                }).execute()
        
        except Exception as e:
            logger.error(f"Error upserting daily sales: {e}")


# Global instance
google_sheets_importer = GoogleSheetsImporter()
