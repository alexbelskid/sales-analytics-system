from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class PivotCell(BaseModel):
    """Single cell in pivot table"""
    dimensions: Dict[str, str]  # e.g. {"product": "Product A", "region": "Минск"}
    revenue: float
    quantity: float
    orders: int
    avg_check: float


class PivotResponse(BaseModel):
    """Pivot table response"""
    data: List[PivotCell]
    total_revenue: float
    total_quantity: float
    total_orders: int
    dimensions_used: List[str]


@router.get("/pivot", response_model=PivotResponse)
async def get_pivot_table(
    period_start: date = Query(..., description="Начало периода"),
    period_end: date = Query(..., description="Конец периода"),
    dimensions: str = Query(..., description="Измерения через запятую: product,customer,agent,region,period"),
    limit: int = Query(default=100, ge=1, le=1000, description="Максимум строк")
):
    """
    Pivot Table (Свод) - многомерная агрегация данных.
    
    Поддерживаемые измерения:
    - product: Группировка по товару
    - customer: Группировка по клиенту
    - agent: Группировка по агенту
    - region: Группировка по региону (из customers)
    - period: Группировка по периоду (month/week/day)
    - category: Группировка по категории товара
    
    Пример: dimensions=product,region
    """
    if supabase is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # Parse dimensions
        dim_list = [d.strip() for d in dimensions.split(",") if d.strip()]
        if not dim_list:
            raise HTTPException(status_code=400, detail="At least one dimension required")
        
        valid_dims = {"product", "customer", "agent", "region", "period", "category"}
        invalid = set(dim_list) - valid_dims
        if invalid:
            raise HTTPException(status_code=400, detail=f"Invalid dimensions: {invalid}")
        
        # Build SELECT clause
        select_fields = ["total_amount", "quantity", "sale_date"]
        
        # Add dimension fields
        if "product" in dim_list:
            select_fields.append("product_id")
        if "customer" in dim_list:
            select_fields.append("customer_id")
        if "agent" in dim_list:
            select_fields.append("agent_id")
        
        # Get sales data
        query = supabase.table("sales").select(",".join(select_fields))
        query = query.gte("sale_date", period_start.isoformat())
        query = query.lte("sale_date", period_end.isoformat())
        
        sales_result = query.execute()
        
        if not sales_result.data:
            return PivotResponse(
                data=[],
                total_revenue=0,
                total_quantity=0,
                total_orders=0,
                dimensions_used=dim_list
            )
        
        # Get lookup data for dimensions
        lookups = {}
        
        if "product" in dim_list or "category" in dim_list:
            products_result = supabase.table("products").select("id, name, category").execute()
            lookups["products"] = {p["id"]: p for p in (products_result.data or [])}
        
        if "customer" in dim_list or "region" in dim_list:
            customers_result = supabase.table("customers").select("id, name, region").execute()
            lookups["customers"] = {c["id"]: c for c in (customers_result.data or [])}
        
        if "agent" in dim_list:
            agents_result = supabase.table("agents").select("id, name").execute()
            lookups["agents"] = {a["id"]: a for a in (agents_result.data or [])}
        
        # Aggregate data
        aggregated = {}
        
        for sale in sales_result.data:
            # Build dimension key
            dim_values = {}
            
            if "product" in dim_list:
                pid = sale.get("product_id")
                product = lookups.get("products", {}).get(pid, {})
                dim_values["product"] = product.get("name", "Unknown")
            
            if "category" in dim_list:
                pid = sale.get("product_id")
                product = lookups.get("products", {}).get(pid, {})
                dim_values["category"] = product.get("category", "Unknown")
            
            if "customer" in dim_list:
                cid = sale.get("customer_id")
                customer = lookups.get("customers", {}).get(cid, {})
                dim_values["customer"] = customer.get("name", "Unknown")
            
            if "region" in dim_list:
                cid = sale.get("customer_id")
                customer = lookups.get("customers", {}).get(cid, {})
                dim_values["region"] = customer.get("region", "Unknown")
            
            if "agent" in dim_list:
                aid = sale.get("agent_id")
                agent = lookups.get("agents", {}).get(aid, {})
                dim_values["agent"] = agent.get("name", "Unknown")
            
            if "period" in dim_list:
                sale_date = sale.get("sale_date", "")
                # Group by month (YYYY-MM)
                dim_values["period"] = sale_date[:7] if sale_date else "Unknown"
            
            # Create key from dimension values
            key = tuple(sorted(dim_values.items()))
            
            if key not in aggregated:
                aggregated[key] = {
                    "dimensions": dict(dim_values),
                    "revenue": 0,
                    "quantity": 0,
                    "orders": 0
                }
            
            aggregated[key]["revenue"] += float(sale.get("total_amount", 0) or 0)
            aggregated[key]["quantity"] += float(sale.get("quantity", 0) or 0)
            aggregated[key]["orders"] += 1
        
        # Convert to list and sort by revenue
        pivot_data = []
        total_revenue = 0
        total_quantity = 0
        total_orders = 0
        
        for agg in aggregated.values():
            avg_check = agg["revenue"] / agg["orders"] if agg["orders"] > 0 else 0
            
            pivot_data.append(PivotCell(
                dimensions=agg["dimensions"],
                revenue=round(agg["revenue"], 2),
                quantity=round(agg["quantity"], 2),
                orders=agg["orders"],
                avg_check=round(avg_check, 2)
            ))
            
            total_revenue += agg["revenue"]
            total_quantity += agg["quantity"]
            total_orders += agg["orders"]
        
        # Sort by revenue descending
        pivot_data.sort(key=lambda x: x.revenue, reverse=True)
        
        # Limit results
        pivot_data = pivot_data[:limit]
        
        return PivotResponse(
            data=pivot_data,
            total_revenue=round(total_revenue, 2),
            total_quantity=round(total_quantity, 2),
            total_orders=total_orders,
            dimensions_used=dim_list
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pivot table error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
