"""
Google Sheets Importer Service
Imports agent sales data from Google Sheets (Продажи ТМ format)
"""

from __future__ import annotations
from typing import List, Dict, Any, Tuple
from datetime import date, datetime, timedelta
import logging
import re

from app.database import supabase
from app.models.agent_analytics import GoogleSheetsImportResult

logger = logging.getLogger(__name__)


class GoogleSheetsImporter:
    """Service for importing agent data from Google Sheets (Продажи ТМ format)"""
    
    # Географические регионы Беларуси
    REGIONS = [
        'БРЕСТ', 
        'ВИТЕБСК', 
        'ГОМЕЛЬ', 
        'ГРОДНО', 
        'МИНСК',
        'МИНСКАЯ ОБЛАСТЬ',
        'МОГИЛЕВ',
        'МОГИЛЁВ'
    ]
    
    # Команды/подразделения (НЕ географические регионы)
    TEAMS = [
        'КАМ РЕКИТТ',
        'МИНСК КА',
        'МИНСК МФЗ',
        'ЮМС',
        'ЮМСА',
        'ГУМИНСКАЯ ЕВГ'
    ]
    
    # Все допустимые значения для поля "регион" (включая команды)
    ALL_REGION_HEADERS = REGIONS + TEAMS
    
    def __init__(self):
        self.supabase = supabase
    
    async def import_from_data(
        self,
        data: List[List[Any]],
        period_start: date,
        period_end: date,
        filename: str = None
    ) -> GoogleSheetsImportResult:
        """
        Import agent data from parsed Google Sheets data
        
        Expected format (from "Продажи ТМ"):
        Таблица "Торговые марки пользователей по регионам" (строки ~71-364)
        
        Иерархия:
        - РЕГИОН (жёлтый фон): колонка A = название региона/команды, колонка B = пусто
        - Агент (голубой фон): колонка A = имя агента, колонка B = пусто, есть данные плана/продаж
        - Бренд (белый фон): колонка A = пусто, колонка B = название бренда
        
        Columns:
        A: Регион / Пользователь
        B: Торговая марка
        C: План продаж
        D: Продажи
        E: % выполнения
        F+: Дополнительные данные
        """
        try:
            agents_imported = 0
            plans_imported = 0
            daily_sales_imported = 0
            brands_imported = 0
            errors = []
            processed_agents = {}  # {agent_name: {region, total_plan, total_sales, brands: []}}
            
            current_region = None
            current_agent = None
            
            logger.info(f"Starting import of {len(data)} rows")
            
            # Find the header row first
            header_row_idx = None
            for row_idx, row in enumerate(data):
                if not row or len(row) == 0:
                    continue
                # Check both first and second columns for header keywords
                first_cell = str(row[0]).strip().upper() if row[0] else ""
                second_cell = str(row[1]).strip().upper() if len(row) > 1 and row[1] else ""
                if ('РЕГИОН' in first_cell or 'ПОЛЬЗОВАТЕЛЬ' in first_cell or
                    'РЕГИОН' in second_cell or 'ПОЛЬЗОВАТЕЛЬ' in second_cell):
                    header_row_idx = row_idx
                    logger.info(f"Found header row at index {row_idx}")
                    break
            
            if header_row_idx is None:
                logger.warning("Header row not found, starting from row 0")
                header_row_idx = 0
            
            # Process data starting after header
            for row_idx in range(header_row_idx + 1, len(data)):
                row = data[row_idx]
                
                if not row or len(row) < 2:
                    continue
                
                col_a = str(row[0]).strip() if row[0] else ""
                col_b = str(row[1]).strip() if row[1] else ""
                
                # Skip empty rows
                if not col_a and not col_b:
                    continue
                
                col_a_upper = col_a.upper()
                col_b_upper = col_b.upper()
                
                # ========================================
                # Case 1: REGION/TEAM header row
                # Either: (col_a filled + col_b empty) OR (col_a empty + col_b filled + col_c empty)
                # ========================================
                if (col_a and not col_b) or (not col_a and col_b and (len(row) <= 2 or not row[2])):
                    # Determine which column has the data
                    data_col = col_a if col_a else col_b
                    data_col_upper = data_col.upper()
                    # Column offset: if data in col_b, plan/sales are in cols D/E (indices 3/4)
                    col_offset = 1 if not col_a and col_b else 0
                    
                    # Check if it's a region or team header
                    is_region_header = any(region in data_col_upper for region in self.ALL_REGION_HEADERS)
                    
                    if is_region_header:
                        # Save current agent before switching regions
                        if current_agent:
                            await self._save_agent_data(
                                current_agent, 
                                processed_agents, 
                                period_start, 
                                period_end
                            )
                            current_agent = None
                        
                        current_region = data_col
                        logger.info(f"Row {row_idx}: Found region/team header: {current_region}")
                        continue
                    
                    # Check if it's an AGENT row
                    plan = self._parse_float(row[2 + col_offset] if len(row) > 2 + col_offset else None)
                    sales = self._parse_float(row[3 + col_offset] if len(row) > 3 + col_offset else None)
                    
                    # Skip if it looks like a header or summary row
                    skip_keywords = ['ИТОГО', 'TOTAL', 'ВСЕГО', 'ОБЩИЙ', 'ПЛАН', 'ПРОДАЖИ', 
                                   'РЕГИОН', 'ПОЛЬЗОВАТЕЛЬ', 'ВЫПОЛНЕНИЕ', 'МАРКА']
                    if any(kw in data_col_upper for kw in skip_keywords):
                        logger.debug(f"Row {row_idx}: Skipping header/summary: {data_col}")
                        continue
                    
                    # Check if it has letters (is a name)
                    has_letters = any(c.isalpha() for c in data_col)
                    if not has_letters:
                        continue
                    
                    # This is an AGENT row
                    if plan is not None or sales is not None:
                        # Save previous agent
                        if current_agent:
                            await self._save_agent_data(
                                current_agent, 
                                processed_agents, 
                                period_start, 
                                period_end
                            )
                        
                        agent_name = data_col
                        current_agent = {
                            'name': agent_name,
                            'region': current_region or 'Unknown',
                            'total_plan': plan or 0,
                            'total_sales': sales or 0,
                            'brands': [],
                            'col_offset': col_offset  # Store for brand parsing
                        }
                        
                        logger.info(f"Row {row_idx}: Found agent '{agent_name}' in {current_region}, plan={plan}, sales={sales}")
                        continue
                
                # ========================================
                # Case 2: BRAND row
                # Brand in col_b (if col_a has data) OR col_c (if col_b has data)
                # ========================================
                elif not col_a and col_b or (col_a and col_b):
                    # Determine brand column based on data structure
                    col_offset = current_agent.get('col_offset', 0) if current_agent else 0
                    brand_col_idx = 1 + col_offset
                    brand_name = row[brand_col_idx] if len(row) > brand_col_idx and row[brand_col_idx] else None
                    
                    if brand_name and current_agent:
                        brand_name = str(brand_name).strip()
                        brand_plan = self._parse_float(row[2 + col_offset] if len(row) > 2 + col_offset else None) or 0
                        brand_sales = self._parse_float(row[3 + col_offset] if len(row) > 3 + col_offset else None) or 0
                        
                        current_agent['brands'].append({
                            'name': brand_name,
                            'plan': brand_plan,
                            'sales': brand_sales
                        })
                        
                        logger.debug(f"Row {row_idx}: Brand '{brand_name}' for agent {current_agent['name']}, sales={brand_sales}")
                        brands_imported += 1
                    elif brand_name:
                        logger.warning(f"Row {row_idx}: Found brand '{brand_name}' but no current agent")
            
            # Save last agent
            if current_agent:
                await self._save_agent_data(
                    current_agent, 
                    processed_agents, 
                    period_start, 
                    period_end
                )
            
            # Count results
            agents_imported = len(processed_agents)
            for agent_data in processed_agents.values():
                if agent_data.get('plan_saved'):
                    plans_imported += 1
                daily_sales_imported += agent_data.get('sales_records_count', 0)
            
            logger.info(f"Import complete: {agents_imported} agents, {plans_imported} plans, {daily_sales_imported} sales, {brands_imported} brands")
            
            # Create import_history record for tracking
            import_id = None
            try:
                from datetime import datetime
                
                # Collect all agent IDs
                agent_ids = [agent_data.get('agent_id') for agent_data in processed_agents.values() if agent_data.get('agent_id')]
                
                # Collect unique regions
                regions = list(set(agent_data.get('region', 'Unknown') for agent_data in processed_agents.values()))
                
                # Create metadata
                metadata = {
                    'period_start': period_start.isoformat(),
                    'period_end': period_end.isoformat(),
                    'regions': regions,
                    'brands_count': brands_imported,
                    'total_rows_processed': len(data)
                }
                
                # Generate filename if not provided
                if not filename:
                    filename = f"Google Sheets Import - {period_start} to {period_end}"
                
                # Insert into import_history
                result = self.supabase.table('import_history').insert({
                    'filename': filename,
                    'file_size': 0,  # Not applicable for Google Sheets
                    'total_rows': len(data),
                    'imported_rows': daily_sales_imported,
                    'failed_rows': 0,
                    'status': 'completed',
                    'progress_percent': 100,
                    'import_source': 'google_sheets',
                    'import_type': 'agents',
                    'metadata': metadata,
                    'related_agent_ids': agent_ids,
                    'started_at': datetime.now().isoformat(),
                    'completed_at': datetime.now().isoformat()
                }).execute()
                
                if result.data and len(result.data) > 0:
                    import_id = result.data[0]['id']
                    logger.info(f"Created import_history record: {import_id}")
            
            except Exception as e:
                logger.error(f"Failed to create import_history record: {e}")
                # Don't fail the import if history creation fails
            
            return GoogleSheetsImportResult(
                success=True,
                agents_imported=agents_imported,
                plans_imported=plans_imported,
                daily_sales_imported=daily_sales_imported,
                errors=errors,
                message=f"Успешно импортировано: {agents_imported} агентов, {plans_imported} планов, {daily_sales_imported} записей продаж, {brands_imported} брендов",
                import_id=import_id
            )
        
        except Exception as e:
            logger.error(f"Import error: {e}")
            return GoogleSheetsImportResult(
                success=False,
                errors=[str(e)],
                message=f"Ошибка импорта: {str(e)}",
                import_id=None
            )
    
    async def _save_agent_data(
        self, 
        agent_data: Dict[str, Any], 
        processed_agents: Dict[str, Any],
        period_start: date,
        period_end: date
    ):
        """Save agent data to database"""
        agent_name = agent_data['name']
        
        # Skip if already processed
        if agent_name in processed_agents:
            logger.warning(f"Agent {agent_name} already processed, skipping")
            return
        
        try:
            # Create or update agent
            agent_id = await self._upsert_agent(agent_name, agent_data['region'])
            if not agent_id:
                logger.error(f"Failed to upsert agent {agent_name}")
                return
            
            # Save sales plan
            plan_saved = False
            if agent_data['total_plan'] and agent_data['total_plan'] > 0:
                await self._upsert_sales_plan(
                    agent_id, 
                    period_start, 
                    period_end, 
                    agent_data['total_plan'], 
                    agent_data['region']
                )
                plan_saved = True
            
            # Save daily sales records for each brand
            # FIX: Use period_end instead of today to ensure data is queryable by dashboard
            sales_records_count = 0
            sale_date = period_end  # Use period end date for sales records
            
            for brand in agent_data['brands']:
                if brand['sales'] and brand['sales'] > 0:
                    await self._upsert_daily_sales(
                        agent_id,
                        sale_date,  # Fixed: use period_end instead of today
                        brand['sales'],
                        agent_data['region'],
                        brand['name']
                    )
                    sales_records_count += 1
            
            # Also save total sales if we have it
            if agent_data['total_sales'] and agent_data['total_sales'] > 0:
                await self._upsert_daily_sales(
                    agent_id,
                    sale_date,  # Fixed: use period_end instead of today
                    agent_data['total_sales'],
                    agent_data['region'],
                    'General'
                )
                sales_records_count += 1
            
            # Mark as processed
            processed_agents[agent_name] = {
                **agent_data,
                'agent_id': agent_id,
                'plan_saved': plan_saved,
                'sales_records_count': sales_records_count
            }
            
            logger.info(f"Saved agent {agent_name}: {sales_records_count} sales records")
        
        except Exception as e:
            logger.error(f"Error saving agent {agent_name}: {e}")
    
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
