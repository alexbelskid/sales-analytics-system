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
    
    # Regional headers that indicate new region section
    REGIONAL_HEADERS = ['БРЕСТ', 'ВИТЕБСК', 'ГОМЕЛЬ', 'ГРОДНО', 'МИНСК', 'МИН']
    
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
            
            current_region = None
            
            for row_idx, row in enumerate(data):
                if not row or len(row) == 0:
                    continue
                
                # Check if this is a regional header
                first_cell = str(row[0]).strip().upper()
                if first_cell in self.REGIONAL_HEADERS or any(reg in first_cell for reg in self.REGIONAL_HEADERS):
                    current_region = first_cell
                    logger.info(f"Found region header: {current_region}")
                    continue
                
                # Skip header rows (contains "Продажи", "План", etc.)
                if any(header in str(row[0:5]).upper() for header in ['ПРОДАЖИ', 'ПЛАН', 'ВЫПОЛН', 'ПРОГНОЗ']):
                    continue
                
                # Try to parse agent row
                try:
                    agent_name = str(row[0]).strip() if row[0] else None
                    
                    if not agent_name or len(agent_name) < 3:
                        continue
                    
                    # Skip summary rows (Итого, Total, etc.)
                    if any(word in agent_name.upper() for word in ['ИТОГО', 'TOTAL', 'ВСЕГО']):
                        continue
                    
                    # Parse sales data
                    sales = self._parse_float(row[1] if len(row) > 1 else None)
                    plan = self._parse_float(row[2] if len(row) > 2 else None)
                    fulfillment_pct = self._parse_float(row[3] if len(row) > 3 else None)
                    forecast_pct = self._parse_float(row[4] if len(row) > 4 else None)
                    
                    # Parse special categories (БелПочта, Потребкооперация, ПИРОТЕХНИКА)
                    belpochta = self._parse_float(row[5] if len(row) > 5 else None) or 0
                    potrebkoop = self._parse_float(row[6] if len(row) > 6 else None) or 0
                    pyrotech = self._parse_float(row[7] if len(row) > 7 else None) or 0
                    
                    # Parse daily history (columns 1-7 after special categories)
                    daily_history = []
                    for i in range(8, min(15, len(row))):  # Typically columns 8-14
                        val = self._parse_float(row[i])
                        if val is not None and val > 0:
                            daily_history.append(val)
                    
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
                                agent_id, today, belpochta, current_region, 'БелПочта'
                            )
                            daily_sales_imported += 1
                        
                        if potrebkoop > 0:
                            await self._upsert_daily_sales(
                                agent_id, today, potrebkoop, current_region, 'Потребкооперация'
                            )
                            daily_sales_imported += 1
                        
                        if pyrotech > 0:
                            await self._upsert_daily_sales(
                                agent_id, today, pyrotech, current_region, 'ПИРОТЕХНИКА'
                            )
                            daily_sales_imported += 1
                        
                        # Import historical daily data if available
                        for day_idx, daily_val in enumerate(daily_history, 1):
                            hist_date = period_start + timedelta(days=day_idx - 1)
                            if hist_date <= period_end:
                                await self._upsert_daily_sales(
                                    agent_id, hist_date, daily_val, current_region, 'General'
                                )
                                daily_sales_imported += 1
                
                except Exception as row_error:
                    error_msg = f"Error processing row {row_idx}: {str(row_error)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    continue
            
            return GoogleSheetsImportResult(
                success=True,
                agents_imported=agents_imported,
                plans_imported=plans_imported,
                daily_sales_imported=daily_sales_imported,
                errors=errors,
                message=f"Successfully imported {agents_imported} agents, {plans_imported} plans, {daily_sales_imported} daily sales records"
            )
        
        except Exception as e:
            logger.error(f"Import error: {e}")
            return GoogleSheetsImportResult(
                success=False,
                errors=[str(e)],
                message=f"Import failed: {str(e)}"
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
