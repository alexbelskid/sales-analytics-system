from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class ScenarioInput(BaseModel):
    """What-If scenario input parameters"""
    price_change_pct: float = 0  # % change in price
    volume_change_pct: float = 0  # % change in volume/quantity
    cost_change_pct: float = 0  # % change in costs (for margin)
    new_customers_pct: float = 0  # % growth in customer base


class ScenarioResult(BaseModel):
    """What-If scenario result"""
    scenario_name: str
    base_revenue: float
    projected_revenue: float
    revenue_change: float
    revenue_change_pct: float
    base_orders: int
    projected_orders: int
    base_avg_check: float
    projected_avg_check: float
    impact_breakdown: dict


class WhatIfResponse(BaseModel):
    """What-If analysis response"""
    base_metrics: dict
    scenarios: List[ScenarioResult]
    period_days: int


@router.post("/what-if", response_model=WhatIfResponse)
async def calculate_what_if(
    scenario: ScenarioInput,
    days: int = Query(default=30, ge=7, le=365, description="Базовый период для расчёта")
):
    """
    What-If сценарный анализ.
    
    Позволяет смоделировать влияние изменений:
    - Цены (price_change_pct)
    - Объёма продаж (volume_change_pct)
    - Затрат (cost_change_pct)
    - Клиентской базы (new_customers_pct)
    
    Возвращает проекцию выручки с разбивкой на факторы влияния.
    """
    if supabase is None:
        return WhatIfResponse(
            base_metrics={},
            scenarios=[],
            period_days=days
        )
    
    try:
        # Get base period metrics
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        sales_result = supabase.table("sales").select(
            "total_amount, quantity, customer_id"
        ).gte("sale_date", start_date.isoformat()).lte("sale_date", end_date.isoformat()).execute()
        
        if not sales_result.data:
            return WhatIfResponse(
                base_metrics={"revenue": 0, "orders": 0, "customers": 0, "avg_check": 0},
                scenarios=[],
                period_days=days
            )
        
        # Calculate base metrics
        base_revenue = sum(float(s.get("total_amount", 0) or 0) for s in sales_result.data)
        base_orders = len(sales_result.data)
        base_quantity = sum(float(s.get("quantity", 0) or 0) for s in sales_result.data)
        base_customers = len(set(s.get("customer_id") for s in sales_result.data if s.get("customer_id")))
        base_avg_check = base_revenue / base_orders if base_orders > 0 else 0
        
        base_metrics = {
            "revenue": round(base_revenue, 2),
            "orders": base_orders,
            "quantity": round(base_quantity, 2),
            "customers": base_customers,
            "avg_check": round(base_avg_check, 2)
        }
        
        # Calculate scenario impact
        price_multiplier = 1 + (scenario.price_change_pct / 100)
        volume_multiplier = 1 + (scenario.volume_change_pct / 100)
        customer_multiplier = 1 + (scenario.new_customers_pct / 100)
        
        # Revenue = Price × Volume × Customers (simplified model)
        # Price change affects average check
        # Volume change affects quantity per order
        # Customer change affects number of orders
        
        projected_avg_check = base_avg_check * price_multiplier
        projected_orders = int(base_orders * customer_multiplier)
        projected_revenue = projected_avg_check * projected_orders * volume_multiplier
        
        revenue_change = projected_revenue - base_revenue
        revenue_change_pct = (revenue_change / base_revenue * 100) if base_revenue > 0 else 0
        
        # Break down impact by factor
        price_impact = base_revenue * (price_multiplier - 1)
        volume_impact = base_revenue * price_multiplier * (volume_multiplier - 1)
        customer_impact = base_revenue * price_multiplier * volume_multiplier * (customer_multiplier - 1)
        
        impact_breakdown = {
            "price_impact": round(price_impact, 2),
            "volume_impact": round(volume_impact, 2),
            "customer_impact": round(customer_impact, 2),
            "total_impact": round(revenue_change, 2)
        }
        
        # Build scenario name
        parts = []
        if scenario.price_change_pct != 0:
            parts.append(f"Price {'+' if scenario.price_change_pct > 0 else ''}{scenario.price_change_pct}%")
        if scenario.volume_change_pct != 0:
            parts.append(f"Volume {'+' if scenario.volume_change_pct > 0 else ''}{scenario.volume_change_pct}%")
        if scenario.new_customers_pct != 0:
            parts.append(f"Customers {'+' if scenario.new_customers_pct > 0 else ''}{scenario.new_customers_pct}%")
        
        scenario_name = ", ".join(parts) if parts else "No changes"
        
        scenarios = [
            ScenarioResult(
                scenario_name=scenario_name,
                base_revenue=round(base_revenue, 2),
                projected_revenue=round(projected_revenue, 2),
                revenue_change=round(revenue_change, 2),
                revenue_change_pct=round(revenue_change_pct, 2),
                base_orders=base_orders,
                projected_orders=projected_orders,
                base_avg_check=round(base_avg_check, 2),
                projected_avg_check=round(projected_avg_check, 2),
                impact_breakdown=impact_breakdown
            )
        ]
        
        return WhatIfResponse(
            base_metrics=base_metrics,
            scenarios=scenarios,
            period_days=days
        )
        
    except Exception as e:
        logger.error(f"What-If analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/what-if/presets")
async def get_scenario_presets():
    """
    Готовые сценарии для What-If анализа.
    """
    return {
        "presets": [
            {
                "name": "Рост цен 10%",
                "description": "Повышение цен на 10% при сохранении объёмов",
                "params": {"price_change_pct": 10, "volume_change_pct": -5}
            },
            {
                "name": "Агрессивный рост",
                "description": "Снижение цен для увеличения объёмов",
                "params": {"price_change_pct": -15, "volume_change_pct": 30}
            },
            {
                "name": "Расширение базы",
                "description": "Привлечение 20% новых клиентов",
                "params": {"new_customers_pct": 20}
            },
            {
                "name": "Кризисный сценарий",
                "description": "Падение объёмов и клиентов на 30%",
                "params": {"volume_change_pct": -30, "new_customers_pct": -20}
            },
            {
                "name": "Оптимистичный",
                "description": "Рост по всем направлениям",
                "params": {"price_change_pct": 5, "volume_change_pct": 15, "new_customers_pct": 10}
            }
        ]
    }
