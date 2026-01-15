from fastapi import APIRouter, Query, HTTPException
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel
from app.database import supabase
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class PlanFactMetric(BaseModel):
    """Plan-Fact comparison for a single metric"""
    metric_name: str
    planned: float
    actual: float
    variance: float  # actual - planned
    variance_pct: float  # (actual - planned) / planned * 100
    completion_pct: float  # actual / planned * 100


class PlanFactResponse(BaseModel):
    """Plan-Fact analysis response"""
    period_start: date
    period_end: date
    metrics: List[PlanFactMetric]
    overall_completion: float
    has_plan: bool


@router.get("/plan-fact", response_model=PlanFactResponse)
async def get_plan_fact_analysis(
    period_start: date = Query(..., description="Начало периода"),
    period_end: date = Query(..., description="Конец периода"),
    product_id: Optional[str] = Query(None, description="ID продукта"),
    customer_id: Optional[str] = Query(None, description="ID клиента"),
    agent_id: Optional[str] = Query(None, description="ID агента"),
    region: Optional[str] = Query(None, description="Регион"),
    category: Optional[str] = Query(None, description="Категория")
):
    """
    Plan-Fact анализ: сравнение плановых и фактических показателей.
    
    Возвращает:
    - Плановые значения (из sales_plans)
    - Фактические значения (из sales)
    - Отклонение (variance)
    - % выполнения плана
    """
    if supabase is None:
        raise HTTPException(status_code=500, detail="Database not available")
    
    try:
        # 1. Get planned metrics - handle schema variations gracefully
        planned_revenue = 0
        planned_quantity = 0
        planned_orders = 0
        has_plan = False
        
        try:
            # Try to query sales_plans table (handles both schema variants)
            plan_result = supabase.table("sales_plans").select("*").execute()
            
            # Filter by period manually since column names may vary
            for p in plan_result.data:
                plan_period = p.get("period") or p.get("period_start")
                if plan_period:
                    from datetime import datetime as dt
                    if isinstance(plan_period, str):
                        try:
                            plan_date = dt.fromisoformat(plan_period.replace("Z", "")).date()
                        except:
                            continue
                    else:
                        plan_date = plan_period
                    
                    if period_start <= plan_date <= period_end:
                        # Handle both column naming conventions
                        planned_revenue += float(p.get("planned_amount", 0) or p.get("planned_revenue", 0) or 0)
                        planned_quantity += int(p.get("planned_quantity", 0) or 0)
                        planned_orders += int(p.get("planned_orders", 0) or 0)
                        has_plan = True
        except Exception as plan_error:
            # sales_plans table may not exist or have different schema - continue with defaults
            logger.warning(f"Could not query sales_plans: {plan_error}")
            has_plan = False
        
        # 2. Get actual metrics
        actual_query = supabase.table("sales").select("total_amount, quantity")
        actual_query = actual_query.gte("sale_date", period_start.isoformat())
        actual_query = actual_query.lte("sale_date", period_end.isoformat())
        
        if product_id:
            actual_query = actual_query.eq("product_id", product_id)
        if customer_id:
            actual_query = actual_query.eq("customer_id", customer_id)
        if agent_id:
            actual_query = actual_query.eq("agent_id", agent_id)
        
        actual_result = actual_query.execute()
        
        # Aggregate actual metrics
        actual_revenue = sum(float(s.get("total_amount", 0) or 0) for s in actual_result.data)
        actual_quantity = sum(float(s.get("quantity", 0) or 0) for s in actual_result.data)
        actual_orders = len(actual_result.data)
        
        # 3. Calculate variances
        def calc_variance(actual: float, planned: float):
            variance = actual - planned
            variance_pct = ((actual - planned) / planned * 100) if planned > 0 else 0
            completion_pct = (actual / planned * 100) if planned > 0 else 0
            return variance, variance_pct, completion_pct
        
        metrics = []
        
        # Revenue
        rev_var, rev_var_pct, rev_comp = calc_variance(actual_revenue, planned_revenue)
        metrics.append(PlanFactMetric(
            metric_name="Выручка",
            planned=round(planned_revenue, 2),
            actual=round(actual_revenue, 2),
            variance=round(rev_var, 2),
            variance_pct=round(rev_var_pct, 2),
            completion_pct=round(rev_comp, 2)
        ))
        
        # Quantity
        qty_var, qty_var_pct, qty_comp = calc_variance(actual_quantity, planned_quantity)
        metrics.append(PlanFactMetric(
            metric_name="Количество",
            planned=planned_quantity,
            actual=actual_quantity,
            variance=qty_var,
            variance_pct=round(qty_var_pct, 2),
            completion_pct=round(qty_comp, 2)
        ))
        
        # Orders
        ord_var, ord_var_pct, ord_comp = calc_variance(actual_orders, planned_orders)
        metrics.append(PlanFactMetric(
            metric_name="Заказы",
            planned=planned_orders,
            actual=actual_orders,
            variance=ord_var,
            variance_pct=round(ord_var_pct, 2),
            completion_pct=round(ord_comp, 2)
        ))
        
        # Overall completion (weighted by revenue)
        overall_completion = rev_comp if has_plan else 0
        
        return PlanFactResponse(
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
            overall_completion=round(overall_completion, 2),
            has_plan=has_plan
        )
        
    except Exception as e:
        logger.error(f"Plan-Fact analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
